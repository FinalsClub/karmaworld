=========
os-install.rst
==========

This document defines the deployment of the KarmaNotes / karmaworld platform on ubuntu server.


Required packages:
- django-1.4.x
- virtualenv
- python-pip
- memcached

Production Requirements:

- rabbitmq-server
- postgresql-server 9.1.x

## 0. Check out code

   git clone https://github.com/finalsclub/karmaworld.git

## 1. setup virtual environment

   cd $SRC_ROOT
   virtualenv beta
   source beta/bin/activate

a) Development

   pip install -r reqs/dev.txt

b) Production

   pip install -r reqs/prod.txt

Also edit manage.py to reflect dev / prod settings file.

Ex.
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "karmaworld.settings.dev")


## 2. Set up database

a) Development

   ./manage.py syncdb
   ./manage.py migrate djcelery

If notes / apps migrations exist, then:

   ./manage.py schemamigration notes --auto
   ./manage.py schemamigration courses --auto
   
If they do not exist:
  
  ./manage.py schemamigration notes --init
  ./manage.py schemamigration courses --init

b) Production

   sudo apt-get install postgresql-9.1 python-psycopg2
   sudo passwd postgres
   sudo su postgres
   sudo -u postgres createuser -P djkarma
   psql template1
   create database karmanotes owner djkarma encoding 'UTF8';
   #### add this line to your postgres install's /etc/postgresql/9.1/main/pg_hba.conf ####
   local   karmanotes      djkarma                                 md5
   sudo service postgresql restart
   ./manage.py syncdb

Then create a file called karmaworld/secret/db_secret.py with the following defined with:

     PROD_DB_NAME
     PROD_DB_USERNAME
     PROD_DB_PASSWORD

After we have configured postgresql and set our secret db_secret file, we then need to preform
the instructions in the beta section of this document.

## 3. Import previous notes (needs more docs)


## 4. Set up S3 bucket support for
