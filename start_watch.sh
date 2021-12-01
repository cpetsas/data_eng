#!/bin/bash
export PROD=0 # Not a very useful variable because we are not using an external redis server.

# REDIS
export REDIS_ENDPOINT_DEV=localhost
export REDIS_PORT_DEV=6379
export REDIS_ENDPOINT_PROD=localhost
export REDIS_PORT_PROD=6379
# CATALOG
export CATALOG_ENDPOINT_DEV=https://dev-api.dfms.co.uk/catalog
export CATALOG_ENDPOINT_PROD=https://beta-catalog.dfms.co.uk

# MAP AND STATISTICAL
export MS_ENDPOINT_DEV=https://beta-api.dfms.co.uk
export MS_ENDPOINT_PROD=https://beta-api.dfms.co.uk

## IMAGE SIZE
export MAP_W=400
export MAP_H=400

# TEMPLATE
export DEFAULT_TEMPLATE=/home/harry/Desktop/dfms-report/report-dfms/templates/default/template.json

# EMAIL CREDENTIALS
export USER=AKIA5Q7RT4GCNBIKDHXP
export PASS=BJhekuoJff2XryoOZVAAziHxap144XYi3/XaPHQEkPtn

# DB
export DBNAME=dfmsmanagement
export DBUSER=dfmsadmin
export DBPASS=dfmsadmin
export DBHOST=localhost
export DBPORT=5432

# RUN CODE
/home/harry/Desktop/dfms-report/report_env/bin/python /home/harry/Desktop/dfms-report/report-dfms/src/watcher.py
