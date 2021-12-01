import redis
import json
import rq
from model import NetworkCreator
import time


def watch():
	r = redis.StrictRedis(host = 'localhost', port = 6379)
	q = rq.Queue(connection = r)
	while True:
		try:
			print(r.llen('requests'))
			if r.llen('requests') != 0:
				for i in range(r.llen('requests')):
					d = r.lpop('requests')
					d = json.loads(d)
					print(d)
					tasks = d['tasks']
					resources = d['resources']
					dependencies = d['dependencies']
					processor = NetworkCreator(tasks, resources, dependencies)
					job = q.enqueue(processor.generate_everything)
			time.sleep(5)
		except Exception as e:
			print(e)

watch()