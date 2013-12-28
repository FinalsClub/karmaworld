# Storing Secrets

Secrets represent authentication information that we have to specify to our app,
so we do not want to check it into source control.  These are stored as files
in `{project_root}/karmaworld/karmaworld/secrets`.


## drive.py

This file points at a json file and a p12 file. These two files are described in
subsections below.

The `GOOGLE_USER` variable should be set to the email address of the user whose
Google Drive is to be accessed. The Google Drive Service account (defined by
the json file and p12 file) will need permission. See the README for more
information on that subject.

### client_secrets.json

`client_secrets.json` contains metadata about the Google Drive service account.
This file is provided by Google. See here for more information:
https://developers.google.com/console/help/new/#serviceaccounts

### drive.p12

`drive.p12` (downloaded from Google as `crazypantslonghexvalue-privatekey.p12`)
contains a private key which replaces a password. This file is very sensitive.
Ensure it is read-only by the proper user(s) through file system controls.

## db_settings.py

`db_settings.py` sets up variables in `settings/prod.py` for connecting to the
a database.

* `PROD_DB_NAME` should be set to the database name
* `PROD_DB_USERNAME` should be set to the role/user which accesses the database
* `PROD_DB_PASSWORD` should be the password of the above role/user

## filepicker.py

`filepicker.py` contains the Filepicker API key which identifies the server
to the Filepicker service.

## static_s3.py

`static_s3.py` sets up variables in `settings/prod.py` for AWS S3 static file
storage. 

* `DEFAULT_FILE_STORAGE` refers to the Django storage backend to use. Generally
    it should be 'storages.backends.s3boto.S3BotoStorage'
* `AWS_ACCESS_KEY_ID` is an alphanumeric identifier given by AWS.
* `AWS_SECRET_ACCESS_KEY` is an ASCII passkey given by AWS.
* `AWS_STORAGE_BUCKET_NAME` is some bucket.
* `S3_URL` is the URL to the s3 bucket (`http://BUCKET.s3.amazonaws.com/`)
* `STATIC_URL` should be the same as the `S3_URL`

## twitter.py

`twitter.py` is used by celery note tasks to send Twitter messages with note
updates.

* `CONSUMER_KEY` is provided by Twitter
* `CONSUMER_SECRET` is provided by Twitter
* `ACCESS_TOKEN_KEY` is provided by Twitter
* `ACCESS_TOKEN_SECRET` is provided by Twitter
