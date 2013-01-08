Database
========

So you've checked out this git repo, and you've set up your virtualenv.
Next you will want to setup your database.


Local development db
--------------------

We use `south <http://south.aeracode.org/wiki/QuickStartGuide>`_ to manage our 
database migrations.

First run a standard django syncdb

    ./manage.py syncdb

And when asked, create a superuser to log into the django-admin.

TODO: Do we need to convert_to_south, or do an initial ``schemamigration --fake``


