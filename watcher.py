import redis
import json
import rq
import generator
import time
import requests
from pprint import pprint
import re
import random
import shutil
import os, sys, traceback
from datetime import datetime
import psycopg2

##########################
# $TODO: WE NEED TO REDO THE HOLE SYSTEM. 
# - Many bugs with different types of dashboards. This script is not considering the different parameters a layer could have.
##########################
def watch(default_template):

	prod = os.environ.get('PROD', 0)

	# Config
	redis_endpoint = None
	redis_port = None
	catalog_url = None
	ms_url = None

	map_w = os.environ.get('MAP_W', 400)
	map_h = os.environ.get('MAP_H', 400)
	
	if prod == 1:
		# Redis
		redis_endpoint = os.environ.get('REDIS_ENDPOINT_DEV', 'localhost')
		redis_port = os.environ.get('REDIS_PORT_DEV', 6379)
		catalog_url = os.environ.get('CATALOG_ENDPOINT_DEV')
		map_url = os.environ.get('MS_ENDPOINT_DEV')

	else:
		redis_endpoint = os.environ.get('REDIS_ENDPOINT_PROD', 'localhost')
		redis_port = os.environ.get('REDIS_PORT_PROD', 6379)
		catalog_url = os.environ.get('CATALOG_ENDPOINT_PROD')
		map_url = os.environ.get('MS_ENDPOINT_PROD')


	r = redis.StrictRedis(host = redis_endpoint, port = redis_port)
	q = rq.Queue(connection = r)

	# Catalog URL
	if catalog_url == None or map_url == None:
		sys.exit(1)

	# Main process: watches the queue and passes the requests to the generator.process function to handle them
	while True:
		try:
			if r.llen('requests') != 0:
				for i in range(r.llen('requests')):
					# Get Dashboard config. New change: Management API will put the dashboard object in the Redis queue insted of the ID (To avoid a new query to the DB or the API).
					d = r.lpop('requests')
					d = json.loads(d)
					dashboard_content = d.get('dashboard')
					dashboard_template = d.get('template')
					email = d.get('email')
					if dashboard_content == None:
						break

					if dashboard_template == None:
						dashboard_template = default_template

					if email == None:
						break

					# Loop Dashboard widgets
					# dash = requests.get('http://0.0.0.0:5000/export/dashboard/' + json.loads(d['id']))
					# content = json.loads(dash.content)

					data = {}
					data['dashboard'] = []
					data['email'] = email
					data['template'] = dashboard_template
					data['dash_id'] = dashboard_content["id"]
					

					counter = 0
					widgets = dashboard_content.get('widgets', [])

					for widget in widgets:
						

						if widget['properties'].get('type') == 'textarea':
							dic = {}
							dic['title'] = widget['properties'].get('title')
							dic['description'] = widget['properties'].get('description')
							dic['type'] = widget['properties'].get('type')
							dic['user_title'] = dashboard_content['title']
							data['dashboard'].append(dic)
						if widget['properties'].get("type") == 'image':
							dic = {}
							dic['type'] = 'image'
							dic['title'] = widget['properties'].get('title')
							dic['description'] = widget['properties'].get('description')
							dic['source'] = widget['properties'].get('src')
							dic['user_title'] = dashboard_content['title']
							response = requests.get(dic['source'], stream=True)
							filename = '/tmp/' + str(datetime.timestamp(datetime.now())).replace('.', '_') + '.png'
							dic['path'] = filename
							with open(filename, 'wb') as out:
								out.write(response.content)
							data['dashboard'].append(dic)
						if widget['properties'].get('type') == 'map' or widget['properties'].get('type') == 'graph':
							dic = {}
							# Get resource information from catalog. This should be remove in new versions (by accessing to the DB directly).
							resource_url = '{}/resources/{}'.format(catalog_url, str(widget['properties'].get('resource').get('id')))
							# print(resource_url)
							request = requests.get(resource_url)
							resource_data = json.loads(request.content)
							# pprint(resource_data)
							# pprint(resource_data)
							api_db_connection = psycopg2.connect(host=os.environ.get('DBHOST'), database=os.environ.get('DBNAME'), user=os.environ.get('DBUSER'), password=os.environ.get('DBPASS'))
							cursor = api_db_connection.cursor()
							# print(data['dash_id'])
							# cursor.execute("SELECT * FROM dashboards where id = %s", (str(data['dash_id']),))
							# user = cursor.fetchone()
							# pprint(user[len(user)-1])
							# Get default unit
							# Get units
							unit = {'key':'', 'label': ''}
							if resource_data['config'].get('units'):
								selected_key =  resource_data['config']['units'].get('default')
								label = selected_key
								values = resource_data['config']['units'].get('values')
								type_resource = resource_data['config']['units'].get('type')
								
								# Get label for default value
								sql = "SELECT label from setting_values WHERE key = '{}'".format(selected_key)
								cursor.execute(sql)
								default_key = cursor.fetchone()
								if default_key != None and len(default_key) > 0:
									label = default_key[0]

								if len(values) > 1 and type_resource != None:
									# Get user units preferences
									sql = 'SELECT us."settingId", us."userId", us.key, sv.label '
									sql += 'FROM user_settings us INNER JOIN setting_values sv ON us."settingId" = sv."settingId" INNER JOIN users u ON u.id = us."userId" '
									sql += 'WHERE us."settingId"=' + "'{}'".format(type_resource) + ' AND u.email = '+"'{}'".format(email) +' AND us.key = sv.key'
									cursor.execute(sql)
									user_settings = cursor.fetchone()
									
									if user_settings != None and len(user_settings) > 0:
										# Check if user_settings for this type of resource is included in the possible values of the resource.
										## Clean key
										key = user_settings[2].replace("/","")
										if key in values:
											label = user_settings[3]
											selected_key = key
								
								unit['key'] = selected_key
								unit['label'] = label
							
							## Get statistics link if exists
							widget_type = widget['properties'].get('type')
							statistics_link = None
							if resource_data['config'].get('statistics') != None:
								statistics_link = resource_data['config']['statistics'].get('link') + "?unit={}".format(unit['key'])

							if statistics_link != None:
								# Graph section
								if widget_type == 'graph':

									## Area preparation - Request formation
									area_details = widget['properties'].get('area').get('geom')
									request_json = {}
									request_json['date'] = widget['properties'].get('resourceParams').get('date')
									if area_details != None:
										if area_details[0].get('geometry') != None:
											area_details[0].get('geometry').update({"crs": {"type":"name", "properties": {"name": "EPSG:4326"}}})
											request_json['area'] = area_details[0]
											# request_json['date'] = widget['properties'].get('resourceParams').get('date')
									else:
										areas_db_connection = psycopg2.connect(host="ec2-35-176-1-183.eu-west-2.compute.amazonaws.com", 
																				database="dfmsgis", user="dfms_read", password="dfms_READ_19@")
										area_id = widget['properties'].get('area').get('idArea')
									
										cursor = areas_db_connection.cursor()
										cursor.execute("SELECT ST_AsGeoJSON(ST_Transform(the_geom, 4326)) as geom FROM boundaries.area where id = %s", (str(area_id),))
										geometry = cursor.fetchone()
										geometry = json.loads(geometry[0])
										cursor.close()
										areas_db_connection.close()
										geom = {}
										geom = {"type": "Feature", "properties":{}}
										geometry.update({"crs": {"type":"name", "properties": {"name": "EPSG:4326"}}})
										geom["geometry"] = geometry
										request_json['area'] = geom

									# Get statistical values
									response = requests.post(statistics_link, json=request_json)
									statistical_values = json.loads(response.content)

									# Prepare Dictionary to create a graph image
									dic['catalog_url'] = catalog_url
									description = resource_data['description']
									description = re.sub(r'\W+', ' ', description)
									dic['title'] = widget['properties'].get('area').get('name')
									dic['description'] = description
									dic['user_description'] = dashboard_content['description']
									dic['updated_at'] = widget['properties'].get('area').get('updatedAt')
									dic['geom'] = area_details
									dic['units'] = unit
									dic['label'] = widget['properties'].get('resource').get('label')
									dic['user_title'] = dashboard_content['title']
									dic['graph_description'] = widget['properties'].get('description')
									dic['values'] = statistical_values

							layer_cretion_link = None
							if resource_data['config'].get('layer_creation') != None:
								layer_cretion_link = resource_data['config']['layer_creation'].get('link')

							if layer_cretion_link != None:
								if widget_type == 'map':
									counter = counter + 1

									dic['geom'] = widget['properties'].get('area').get('geom')
									dic['title'] = widget['properties'].get('area').get('name')
									dic['updated_at'] = widget['properties'].get('area').get('updatedAt')
									dic['label'] = widget['properties'].get('resource').get('label')
									dic['user_description'] = dashboard_content['description']
									dic['user_title'] = dashboard_content['title']
									dic['map_description'] = widget['properties'].get('description')

									description = resource_data['description']
									description = re.sub(r'\W+', ' ', description)
									dic['description'] = description
									
									# Read parameters to create json 
									map_parameters = {}
									widget_params = widget['properties'].get('resourceParams')
									layer_params = resource_data['config'].get('layer_creation').get('params')
									if layer_params != None:
										for param in widget_params:
											if param in widget_params.keys():
												val = widget_params[param]
												if val not in layer_params[param]['values']:
													val = layer_params[param]['values'][-1]
												map_parameters[param] = val
									
									dic['map_parameters'] = map_parameters
									
									request_json = map_parameters
									if dic['geom'] != None:
										dic['geom'][0].get('geometry').update({"crs": {"type":"name", "properties": {"name": "EPSG:4326"}}})
										request_json['area'] = dic['geom'][0]
										request_json['draw_area'] = True
									else:
										areas_db_connection = psycopg2.connect(host="ec2-35-176-1-183.eu-west-2.compute.amazonaws.com", 
																				database="dfmsgis", user="dfms_read", password="dfms_READ_19@")
										area_id = widget['properties'].get('area').get('idArea')
									
										cursor = areas_db_connection.cursor()
										cursor.execute("SELECT ST_AsGeoJSON(ST_Transform(the_geom, 4326)) as geom FROM boundaries.area where id = %s", (str(area_id),))
										geometry = cursor.fetchone()
										geometry = json.loads(geometry[0])
										cursor.close()
										areas_db_connection.close()
										geom = {}
										geom = {"type": "Feature", "properties":{}}
										geometry.update({"crs": {"type":"name", "properties": {"name": "EPSG:4326"}}})
										geom["geometry"] = geometry
										request_json['area'] = geom
										request_json['draw_area'] = True

									layer_request = requests.post(resource_data['config'].get('layer_creation').get('link'), json = request_json)
									response_body = json.loads(layer_request.content)
									layer_ID = response_body['layer_id']
									dic['units'] = unit

									# Get legend
									legend_url = resource_data['config']['legend']['link']
									legend_url = legend_url.replace('{layer_id}', layer_ID) + "?unit={}".format(unit['key'])
									legend_request = requests.get(legend_url)
									dic["legend"] = json.loads(legend_request.content)
									map_picture = pic = requests.get('{}/map/{}/{}/{}.png'.format(map_url, layer_ID, map_w, map_h))
									map_path = '/tmp/' + str(datetime.timestamp(datetime.now())).replace('.', '_') + '.png'
									with open(map_path, 'wb') as out:
										out.write(pic.content)

									dic['path'] = os.path.abspath(map_path)
							dic['type'] = widget_type
							data['dashboard'].append(dic)
					q.enqueue(generator.process, data)
			time.sleep(3)
		except Exception as e:
			traceback.print_exc()

if __name__ == '__main__':
	default_template = os.environ.get('DEFAULT_TEMPLATE')
	if default_template == None:
		# Exit
		sys.exit(1)
	watch(default_template)