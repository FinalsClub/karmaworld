# KarmaWorld
__Description__: A django application for sharing and uploading class notes.

__Copyright__: FinalsClub, a 501c3 non-profit organization

__License__: GPLv3 except where otherwise noted

__Contact__: info@karmanotes.org

v3.0 of the karmanotes.org website from the FinalsClub Foundation

# Purpose

KarmaNotes is an online database of college lecture notes.  KarmaNotes empowers college students to participate in the free exchange of knowledge. 

# Pre-Installation

## Code

Before doing anything, you'll need the code. Grab it from github.

Clone the project from the central repo using your github account:

    git clone git@github.com:FinalsClub/karmaworld.git

If you aren't using a system setup for github, then grab the project with
this command instead:

    git clone https://github.com/FinalsClub/karmaworld.git

Generally speaking, this will create a subdirectory called `karmaworld` under
the directory where the `git` command was run. This git repository directory
will be referred to herein as `{project_root}`.

There might be some confusion as the git repository's directory will likely be
called `karmaworld` (this is `{project_root}`), but there is also a `karmaworld`
directory underneath that (`{project_root}/karmaworld`) alongside files like
`fabfile.py` (`{project_root}/fabfile.py`) and `README.md`
(`{project_root}/README.md`).

## External Service Dependencies

Notice: This software makes use of external third party services which require
accounts to access the service APIs. Without these third parties available,
this software may require considerable overhaul. These services have
API keys that you must provide to KarmaNotes as environment variables. The
best way to do this is by using a `.env` file. Copy `.env.example` to `.env`
and populate the fields as required.

### Filepicker
This software uses [Filepicker.io](https://www.inkfilepicker.com/) for uploading
files. This requires an account with Filepicker.

Filepicker requires an additional third party file hosting site where it may
send uploaded files. For this project, we have used Amazon S3.

Your Filepicker API key must be provided in `FILEPICKER_API_KEY` and your
secret in `FILEPICKER_SECRET`.

### Amazon S3

#### for Filepicker
This software uses [Amazon S3](http://aws.amazon.com/s3/) as a third party file
hosting site. The primary use case is a destination for Filepicker files. The
software won't directly need any S3 information for this use case; it will be
provided directly to Filepicker.

#### for Static File hosting
A secondary use case for S3 is hosting static files. The software will need to
update static files on the S3 bucket. In this case, the software will need the
S3 bucket name, access key, and secret key.

The code assumes S3 is used for static files in a production environment. To
obviate the need for hosting static files through S3 (noting that it still might
be necessary for Filepicker), a workaround was explained [in this Github ticket](https://github.com/FinalsClub/karmaworld/issues/192#issuecomment-30193617).

That workaround is repeated here. Make the following changes to
`{project_root}/karmaworld/settings/prod.py`:

1. comment out everything about static_s3 from imports
2. comment out storages from the `INSTALLED_APPS`
3. change `STATIC_URL` to `'/assets/'`
4. comment out the entire storages section (save for part of `INSTALLED_APPS` and `STATIC_URL`)
5. add this to the nginx config:

    location /assets/ {
        root /var/www/karmaworld/karmaworld/;
    }
    
### IndexDen
KarmaNotes uses IndexDen to create a searchable index of all the notes
in the system. Create an free IndexDen account at [their homepage](http://indexden.com/).
You will be given a private URL that accesses your IndexDen account.
Set the environment variable INDEXDEN_PRIVATE_URL to your private URL and
INDEXDEN_INDEX to the name
of the index you want KarmaNotes to use. The index will be created automatically when
KarmaNotes is run if it doesn't already exist. For example,
```
INDEXDEN_PRIVATE_URL='http://:secretsecret@secret.api.indexden.com'
INDEXDEN_INDEX='karmanotes_something_something'
```

### Google Drive
This software uses [Google Drive](https://developers.google.com/drive/) to
convert documents to and from various file formats.

A Google Drive service account with access to the Google Drive is required.
This may be done with a Google Apps account with administrative privileges, or ask
your business sysadmin.

These are the instructions to create a Google Drive service account:
https://developers.google.com/drive/delegation

When completed, set the environment variables `GOOGLE_CLIENT_SECRETS`,
`GOOGLE_USER`, and `GOOGLE_SERVICE_KEY_BASE64`.

### Twitter

Twitter is used to post updates about new courses. Access to the Twitter API
will be required for this task.

If this Twitter feature is desired, the consumer key and secret as well as the
access token key and secret are needed by the software.

If the required environment variables are not found, then no errors will occur
and no tweets will be posted.

To set this up, create a new Twitter application at https://dev.twitter.com/apps/new.
Make sure this application has read/write access. Generate an access token. Go to your
OAuth settings, and grab the "Consumer key", "Consumer secret", "Access token", and
"Access token secret". Set these to the variables `TWITTER_CONSUMER_KEY`,
`TWITTER_CONSUMER_SECRET`, `TWITTER_ACCESS_TOKEN_KEY`, `TWITTER_ACCESS_TOKEN_SECRET`


### SSL Certificate

If you wish to host your system publicly, you'll need an SSL certificate
signed by a proper authority.

If you are working on local system for development, a self signed certificate
will suffice. There are plenty of resources available for learning how to
create one, so that will not be detailed here. Note that the Vagrant file will
automatically generated a self signed certificate within the virtual machine.

The certificate should be installed using nginx.

# Local Install

KarmaNotes is a Heroku application. Download the [Heroku toolbelt](https://toolbelt.heroku.com/).

To run KarmaNotes locally, do `foreman start`. Before your first run, there are
a few setup steps:
  1. `virtualenv venv`
  1. `source venv/bin/activate`
  1. `pip install -r requirements.txt`
  1. `pip install -r requirements-dev.txt`
  1. `foreman run python manage.py syncdb --migrate --noinput`
  1. `foreman run python manage.py createsuperuser`
  1. `foreman run python manage.py fetch_usde_csv ./schools.csv`
  1. `foreman run python manage.py import_usde _csv ./schools.csv`
  1. `foreman run python manage.py sanitize_usde_schools`


# Heroku Install

KarmaNotes is a Heroku application. Download the [Heroku toolbelt](https://toolbelt.heroku.com/).

To run KarmaNotes on Heroku, do `heroku create` and `git push heroku master` as typical
for a Heroku application. This will deploy KarmaNotes to Heroku with a supporting buildpack.

You will need to import the US Department of Education's list of accredited schools.
   1. Fetch USDE schools with
      `heroku run python manage.py fetch_usde_csv ./schools.csv`
   1. Upload the schools into the database with
      `heroku run python /manage.py import_usde _csv ./schools.csv`
   1. Clean up redundant information with
      `heroku run python /manage.py sanitize_usde_schools`


# Django Database management

## South

We have setup Django to use
[south](http://south.aeracode.org/wiki/QuickStartGuide) for migrations. When
changing models, it is important to run
`foreman run python manage.py schemamigration` which will create a migration
 to reflect the model changes into the database. These changes can be pulled
into the database with `foreman run python manage.py migrate`.

Sometimes the database already has a migration performed on it, but that
information wasn't told to south. There are subtleties to the process which
require looking at the south docs. As a tip, start by looking at the `--fake`
flag.

# Assets from Third Parties

A number of assets have been added to the repository which come from external
sources. It would be difficult to keep a complete list in this README and keep
it up to date. Software which originally came from outside parties can
generally be found in `karmaworld/assets`.

Additionally, all third party Python projects (downloaded and installed with
pip) are listed in these files:

* `requirements.txt`
* `requirements-dev.txt`

# Thanks

* KarmaNotes.org is a project of the FinalsClub Foundation with generous funding from the William and Flora Hewlett Foundation

* Also thanks to [rdegges](https://github.com/rdegges/django-skel) for the django-skel template
