# Bootstrapping a DB

A fresh database may be bootstrapped by running `manage.py syncdb --migrate`.
Initial schools must be populated, which can be done by running:

1. `manage.py fetch_usde_csv ./school.csv`
1. `manage.py import_usde_csv ./school.csv`
1. `manage.py sanitize_usde_schools`

For testing purposes, it might be desirable to populate a database with
additional data. In this case, see
[the next section](#importing-a-preliminary-db).

# Importing a Preliminary DB

A preliminary set of Notes, Courses, and Schools is available as json from 
the [this repository](https://github.com/FinalsClub/notesjson)

## import to a fresh database

To import this db:

1. download or clone the notesjson repo
2. move the contents of the repo to the root of karmanotes
3. run the following management command: `./manage.py import_json all`

## import to a database which has data

Alternatively, you can remove all current Notes, Courses, and Schools from 
the database before importing with the following management command:

    ./manage.py import_json all clean
