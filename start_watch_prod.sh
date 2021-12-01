#!/bin/bash
export PROD=0

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
export DEFAULT_TEMPLATE=/home/ubuntu/report-dfms/templates/default/template.json

# EMAIL CREDENTIALS
export USER=AKIA5Q7RT4GCNBIKDHXP
export PASS=BJhekuoJff2XryoOZVAAziHxap144XYi3/XaPHQEkPtn

# DB
export DBNAME=dfmsmanagement
export DBUSER=dfmsadmin
export DBPASS=dfmsadmin
export DBHOST=dfms-management.cyv8qaegkgmb.eu-west-2.rds.amazonaws.com
export DBPORT=5432

# RUN CODE
/home/ubuntu/report-dfms/env/bin/python /home/ubuntu/report-dfms/src/watcher.py
