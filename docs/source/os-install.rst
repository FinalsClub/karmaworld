os-install.rst
==============

This document defines the deployment of the KarmaNotes / karmaworld platform on ubuntu server.


Required packages:
+ django-1.4.x
+ virtualenv
+ python-pip
+ memcached
+ (See $SRC_ROOT)/reqs/common.py)

Production Requirements:

+ rabbitmq-server
+ postgresql-server 9.1.x
+ ($SRC_ROOT)/reqs/prod.py)

Before we begin, we are going to need a few commonly installed tools:

    sudo apt-get install git-core make gcc libmemcached-dev python-pip
    sudo pip install pip --upgrade # upgrade pip to the latest pip for our version of python
    sudo pip install virtualenv

If we are in a production environment, we need:

      sudo apt-get install rabbitmq-server postgresql-server


0. Check out code
-----------------

   git clone https://github.com/finalsclub/karmaworld.git

Generally, it is advised to have a common $WEB_ROOT.
Ours is in:  `/var/www`
So, for our use case, our $SRC_ROOT is:

    /var/www/karmaworld

Also note that /var/www needs to have proper permissions and creating a separate
user to interact with the app is advised (with basic user permissions).

1. setup environment
--------------------

In a production environment we use the following:

+ ubuntu server 12.04 LTS
+ postgresql-server 9.1.x
+ rabbitmq-server (our broker)
+ python-pip
+ virutalenv
+ django-1.4.3+
+ libmemcached-dev
+ (see $SRC_ROOT/reqs/prod.txt)

Installing virtualenv is advised for both development and production environments.

  sudo pip install virtualenv

We then need to set up a virtual environment so we have a nice container
to work from. This allows regular users to set up a proper environment
without the need of superuser permissions or to install python modules to
the system directly.

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


2. Set up database
------------------

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

Then create a file called karmaworld/secret/db_secret.py. Please see 'secrets.rst' in $SRC_ROOT/docs/source/secrets.rst.

After we have configured postgresql and set our secret db_secret file, we then need to preform
the instructions in the beta section of this document.

3. Import previous notes (needs more docs)
------------------------------------------

4. Set up S3 bucket support (optional)
--------------------------------------

See $SRC_ROOT/docs/source/secrets.rst
