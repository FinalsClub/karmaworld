Importing a Preliminary DB
==========================

A preliminary set of Notes, Courses, and Schools is available as json from 
the following repository:

https://github.com/FinalsClub/notesjson

To import this db:
1. download or clone the notesjson repo
2. move the contents of the repo to the root of karmanotes
3. run the following management command:
./manage.py import_json all


Alternatively, you can remove all current Notes, Courses, and Schools from 
the database before importing with the following management command

./manage.py import_json all clean
