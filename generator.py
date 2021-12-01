# import Template_class
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
import os
import json

# This calls the class to create the report, send the email to the owner of the report and to save it in the S3 bucket
# The content variable is a json request. The email smtp server needs to use 465 port

def process(content):
	# Create report from json request
	pdf = Template_class.DPdf(content)
	pdf.create()
	filename = pdf.name
	report_path = pdf.report_path
	pdf.draw()
	pdf.render()
	# s = smtplib.SMTP()
	# Send email to recipient(s)
	recipients = content['email']
	# for recipient in recipients:
	mail = MIMEMultipart()
	mail['From'] = 'noreply@dfms.co.uk'
	mail['Subject'] = 'DFMS - Report'
	attachment = open(report_path+filename, 'rb')
	e = MIMEBase('application', 'octet-stream')
	e.set_payload((attachment).read())
	encoders.encode_base64(e)
	e.add_header('content-disposition', 'attachment', filename=filename)
	mail.attach(e)
	# s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
	s = smtplib.SMTP('email-smtp.eu-west-1.amazonaws.com')
	s.connect('email-smtp.eu-west-1.amazonaws.com', 587)
	s.starttls()
	# s.set_debuglevel(1)
	s.login('AKIA5Q7RT4GCNBIKDHXP', 'BJhekuoJff2XryoOZVAAziHxap144XYi3/XaPHQEkPtn')
	text = mail.as_string()
	s.sendmail('noreply@dfms.co.uk', recipients, text)
	s.quit()
	# Upload report in amazon S3 and clear local file
	s3 = boto3.resource('s3')
	data = open(report_path+filename, 'rb')
	s3.Bucket('dfms-pdf-reports').put_object(Key=filename, Body=data)
	os.remove(report_path+filename)


# print(str(datetime.datetime.timestamp(datetime.datetime.now())).replace('.', '_'))
# content = json.load(open('content.json'))
# process(content)
