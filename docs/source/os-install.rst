os-install.rst
==============

This document defines the deployment of the KarmaNotes / karmaworld platform on Ubuntu server. 

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

1. Environment Setup
--------------------

First we need to setup our environment to run the app. This includes installing 
necessary dependencies, setting proper config files and creating a new databases 
(if in production).

In a production environment we use the following:

+ ubuntu server 12.04 LTS
+ postgresql-server 9.1.x
+ rabbitmq-server (our broker)
+ python-pip
+ virutalenv
+ django-1.4.3+
+ libmemcached-dev
+ (see $SRC_ROOT/reqs/prod.txt)

In all of our deployments, we use virtualenv to provide a clean way of
installing dependencies and providing a solid environment from which the app can
be run from. It is advised that virtualenv be used for all deployments.

  sudo pip install virtualenv

After installing virtualenv, we need to configure our new environment. Note that
installing packages within the environment does not need superuser permissions.

    cd $SRC_ROOT
    virtualenv beta
    source beta/bin/activate

a) Development

   pip install -r reqs/dev.txt

b) Production

   pip install -r reqs/prod.txt

Once all dependencies have been installed, we need to edit our manage.py file
so that we are reading the proper settings.py file:

a) Development

	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "karmaworld.settings.dev")

b) Production

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "karmaworld.settings.prod")


2. Set up database
------------------

In both development and production we do set up databases, but dev. uses
SQLite out of the box and requires minimal interaction. If in a production 
environment, make sure to follow the instructions in section b first.

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

Materials from previous instances of karmaworld / djKarma can be imported into a new clean database via. json files.
Karmaworld has facilities built-in so that these json files can easily be imported.

To get started, we need to get the .json files:

   git clone https://github.com/FinalsClub/notesjson.git
   mv notesjson/* .

Then we run the imports (in our virtual environment):

   ./manage.py import_json all


4. Set up S3 bucket support (optional)
--------------------------------------

S3 is a storage service that is provided by Amazon. Buckets
are storage lockers where files can be stored and served from.
The reason that we would want to serve files out of said buckets
is so that we can move some traffic from production and provide
a more reliable experience to the user.


See $SRC_ROOT/docs/source/secrets.rst
