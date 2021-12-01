from redis import Redis, StrictRedis
import json
from rq import Queue
from io import StringIO
import sys
from reportPDF import Template_class
import smtplib
import boto3
import calendar
import time
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os, Q_process

# Create a connection to redis Queue
conn = StrictRedis()
# Load the data from json file (currently this json file is local)
# but this will eventually be done on the server by the frontend
content = json.load(open('./report-DFMS/src/reportPDF/content.json'))
# The redis Q doesn't like the output of the load function so I have to dump the contents first
content = json.dumps(content)
# print(content)
content1 = json.load(open('./report-DFMS/src/reportPDF/content1.json'))
content1 = json.dumps(content1)
# Connect to Q
q = Queue(connection=conn)
# Push data in Q. This will be modified because pushing should not be done here
for i in range(1):
	result = q.enqueue(Q_process.process, content)
	# result1 = q.enqueue(process, content1)
