# KarmaWorld
__Description__: A django application for sharing and uploading class notes.

__Copyright__: FinalsClub, a 501c3 non-profit organization

__License__: GPLv3 except where otherwise noted

__Contact__: info@karmanotes.org

v3.0 of the karmanotes.org website from the FinalsClub Foundation

# Purpose

KarmaWorld is an online database of college lecture notes.  KarmaWorld
empowers college students to participate in the free exchange of knowledge.

# Naming

The repository and the project are called KarmaWorld. One implementation
of KarmaWorld, which is run by FinalsClub Foundation, is called
[KarmaNotes](https://www.karmanotes.org/).

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

## External Software Dependencies

### pdf2htmlEX

KarmaWorld uses [pdf2htmlEX](https://github.com/coolwanglu/pdf2htmlEX) as
a dependency. pdf2htmlEX is used to convert uploaded PDF notes into HTML.

An [outdated version of pdf2htmlEX](https://github.com/FinalsClub/pdf2htmlEX)
is available which includes the
[patch](https://github.com/FinalsClub/pdf2htmlEX/commit/3c19f6abd8d59d1b58cf254b7160b332b3f5b517)
required for pdf2htmlEX to correctly work with KarmaWorld.

Newer versions can be used by applying the patch by hand. It's a fairly
simple two-line modification that can be done after installing
pdf2htmlEX.

### SSL Certificate

If you wish to host your system publicly, you'll almost certainly want
an SSL certificate signed by a proper authority.

You may need to set the `SSL_REDIRECT` environment variable to `true` to
make KarmaWorld redirect insecure connections to secure ones.

Follow [Heroku's SSL setup](https://devcenter.heroku.com/articles/ssl-endpoint)
to get SSL running on your server with Heroku.

## External Service Dependencies

Notice: This software makes use of external third party services which require
accounts to access the service APIs. Without these third parties available,
this software may require considerable overhaul. These services have
API keys, credentials, and other information that you must provide to KarmaWorld
as environment variables. The best way to persist these environment variables is
by using a `.env` file.  Copy `.env.example` to `.env` and populate the fields as required.

A number of services are required even if running the KarmaWorld web service
locally, some of the services are recommended, and some are completely optional
even if running the web service on Heroku.

Many of these services have free tiers and can be used without charge for
development testing purposes.

* Reminder
  * Copy `.env.example` to `.env` and populate the environment variables there.
* Required Services
  * [Google Drive](#google-drive)
  * [Filepicker](#filepicker)
  * [PostgreSQL](#postgresql)
  * [Celery](#celery-queue)
* Optional but recommended
  * [IndexDen](#indexden): enables searching through courses, notes, etc
  * [Heroku](#heroku): the production environment used by karmanotes.org
    * it might not be possible to run KarmaWorld on Heroku using a free
      webapp.
  * [Amazon S3](#s3-for-static-files): for static file hosting
* Entirely optional (though used in the production environment)
  * [Twitter](#twitter): share updates about new uploads
  * [Amazon Mechanical Turk](#amazon-mechanical-turk): generate quizzes, flashcards, etc
  * [Amazon CloudFront](#amazon-cloudfront-cdn)
  * [Amazon S3](#s3-for-filepicker): store files uploaded to Filepicker
    * Filepicker does not support S3 storage in its free tier

### Heroku
This project has chosen to use [Heroku](www.heroku.com) to host the Django and
celery software. While not a hard requirement, the more up-to-date parts of this
documentation will operate assuming Heroku is in use.

See README.heroku for more information.

#### pdf2htmlEX on Heroku
If using Heroku, the default
[KarmaNotes Heroku buildpack](https://github.com/FinalsClub/heroku-buildpack-karmanotes)
will [include](https://github.com/FinalsClub/heroku-buildpack-karmanotes/blob/master/bin/steps/pdf2htmlex)
the [required version of pdf2htmlEX](#pdf2htmlex).

### Celery Queue
Celery uses the Apache Message Queueing Protocol for passing messages to its workers.

For production, we recommend using Heroku's CloudAMQP add-on, getting your own CloudAMQP account, or
running a queueing system on your own. The `CLOUDAMQP_URL` environment variable must be set correctly
for KarmaWorld to be able to use Celery. The `CELERY_QUEUE_NAME` environment variable
must be set to the name of the queue you wish to use. Settings this to something unique
allows multiple instances of KarmaWorld (or some other software) to share the same queueing server.

For development on localhost, `RabbitMQ` is the default for `djcelery` and is well supported. Ensure
`RabbitMQ` is installed for local development.

### PostgreSQL

PostgreSQL is not necessarily required; other RDBMS could probably be fit into
place. However, the code was largely written assuming PostgreSQL will be used.
Change to another system with the caveat that it might take some work.

There are many cloud providers which provide PostgreSQL databases. Heroku has
an add-on for providing a PostgreSQL database. Ensure something like this
is made available and installed to the app.

For local development, ensure a PostgreSQL is running on localhost or is
otherwise accessible.

### Amazon S3
The instructions for creating an [S3](http://aws.amazon.com/s3/) bucket may be
[found on Amazon.](http://docs.aws.amazon.com/AmazonS3/latest/gsg/CreatingABucket.html)

Two, separate buckets may be used in production: one for static file hosting
and one as a communication bus with Filepicker.

#### S3 for Filepicker

This software uses S3 to store files which are sent to or received 
from Filepicker. Filepicker will need to know the S3 bucket name, access key,
and secret key.

Filepicker users can only make use of an S3 bucket with a paid account. For
development purposes, no Filepicker S3 bucket is needed. Skip all references to
the Filepicker S3 bucket in the development case.

The software will not need to know the S3 credentials for the Filepicker
bucket, because the software will upload files to the Filepicker S3 bucket
through Filepicker's API and it will link to or download files from the
Filepicker S3 bucket through Filepicker's URLs. This will be covered in the
[Filepicker section](#filepicker).

#### S3 for static files

This software uses S3 for hosting static files. The software will need to
update static files on the S3 bucket. As such, the software will need the
S3 bucket name, access key, and secret key via the environment variables. This
is described in subsections below.

To support static hosting, `DEFAULT_FILE_STORAGE` should be set to
`'storages.backends.s3boto.S3BotoStorage'`, unless there is a compelling reason
to change it.

There are three ways to setup access to the S3 buckets depending upon speed
and security. The more secure, the slower it will be to setup.

#### insecure S3 access
For quick and dirty insecure S3 access, create a single group and a single user
with full access to all buckets. Full access to all buckets is insecure!

Create an 
[Amazon IAM group](http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_CreatingAndListingGroups.html)
with full access to the S3 bucket. Select the "Amazon S3 Full Accesss" Policy
Template.

Create an
[Amazon IAM user](http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_SettingUpUser.html).
Copy the credentials into the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
environment variables. Be sure to write down the access information, as it
will only be shown once.

#### secure S3 access
For secure S3 access, two users will be needed. One with access to the
Filepicker bucket and one with access to the static hosting bucket.

Note: this might need to be modified to prevent creation and deletion of
buckets?

Create an 
[Amazon IAM group](http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_CreatingAndListingGroups.html)
with full access to the S3 bucket. The quick way is to select the
"Amazon S3 Full Accesss" Policy Template and replace `"Resource": "*"` with 
`"Resource": "arn:aws:s3:::<static_bucket_name>"`.

Create an
[Amazon IAM user](http://docs.aws.amazon.com/IAM/latest/UserGuide/Using_SettingUpUser.html).
Copy the credentials into the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
environment variables. Be sure to write down the access information, as it
will only be shown once.

Ensure the created user is a member of the group with access to the S3
static files bucket.

Repeat the process again, creating a group for the Filepicker bucket and
creating a user with access to that group. These credentials will be passed
on to Filepicker.

#### somewhat secure S3 access
Create two groups as described in the `secure S3 access` section above.

Create a single user, save the credentials as described in the
`insecure S3 access` section above, and pass the credentials on to Filepicker.

Add the single user to both groups.

This is less secure because if your web server or Filepicker get compromised
(so there are two points for potential failure), the single compromised
user has full access to both buckets.

### Amazon Cloudfront CDN
[Cloudfront CDN](http://aws.amazon.com/cloudfront/) assists static file hosting.

Follow
[Amazon's instructions](http://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.html)
to host static files out of the appropriate S3 bucket. Note that Django's static
file upload process has been modified to mark static files as publicly
assessible.

In the settings for the Cloudfront Distribution, copy the "Domain Name" from
General settings and set `CLOUDFRONT_DOMAIN` to it. For example, `abcdefghij.cloudfront.net`.

### Amazon Mechanical Turk
Mechanical turk is employed to generate human feedback from uploaded notes.
This service is helpful for generating flash cards and quizzes.

This service is optional and it might cause unexpected charges when
deployed.  If the required environment variable is not found,
then no errors will occur and no mechanical turk tasks will be created, avoiding any unexpected
costs.

The `MTURK_HOST` environment variable is almost certainly
`"mechanicalturk.amazonaws.com"`.

The code will create and publish HITs on your behalf.

### Google Drive
This software uses [Google Drive](https://developers.google.com/drive/) to
convert documents to and from various file formats.

A Google Drive service account with access to the Google Drive is required.
This may be done with a Google Apps account with administrative privileges, or ask
your business sysadmin.

Follow [Google's instructions](https://developers.google.com/drive/delegation)
to create a Google Drive service account.

Convert the p12 file into a Base64 encoded string for the
`GOOGLE_SERVICE_KEY_BASE64` environment variable. There are many ways to do
this. If Python is available, the
[binascii library](https://docs.python.org/2/library/binascii.html#binascii.b2a_base64)
makes this very easy:

        import binascii
        with open('file.p12', 'r') as f:
            print binascii.b2a_base64(f.read)

Copy the contents of `client_secret_*.apps.googleusercontent.com.json` into the
`GOOGLE_CLIENT_SECRETS` environment variable.

### Filepicker
This software uses [Filepicker.io](https://www.inkfilepicker.com/) for uploading
files. This requires an account with Filepicker.

Filepicker can use an additional third party file hosting site where it may
send uploaded files. This project, in production, uses Amazon S3 as the third
party. See the Amazon S3 section above for more information.  

Create a new App with Web SDK and provide the Heroku App URL for the
Application's URL. You'll be given an API Key for the App. Paste this into the
`FILEPICKER_API_KEY` environment variable.

Find the 'App Security' button on the left hand side of the web site. Make sure
'Use Security' is enabled. Generate a new secret key. Paste this key into the
`FILEPICKER_SECRET` environment variable.

If you have an upgraded plan, you can configure Filepicker to have access to
your Filepicker S3 bucket. Click 'Amazon S3' on the left hand side menu and
supply the credentials for the user with access to the Filepicker S3 bucket.

### IndexDen
KarmaWorld uses IndexDen to create a searchable index of all the notes in the
system. Create an free IndexDen account at
[their homepage](http://indexden.com/). You will be given a private URL that
accesses your IndexDen account. This URL is visible on your dashboard (you
might need to scroll down).

Set the `INDEXDEN_PRIVATE_URL` environment variable to your private URL.

Set the `INDEXDEN_INDEX` environment variable to the name of the index you want
to use for KarmaWorld. The index will be created automatically when KarmaNotes
is run if it doesn't already exist. It may be created through the GUI if
desired.

### Twitter

Twitter is used to post updates about new courses. Access to the Twitter API
will be required for this task.

If this Twitter feature is desired, the consumer key and secret as well as the
access token key and secret are needed by the software.

If the required environment variables are not found, then no errors will occur
and no tweets will be posted.

To set this up,
[create a new Twitter application](https://dev.twitter.com/apps/new).
Use your Heroku App URL for the website field. Leave the Callback field blank.

Make sure this application has read/write access. Generate an access token. Go
to your OAuth settings, and grab the "Consumer key", "Consumer secret",
"Access token", and "Access token secret". Paste these, respectively, into the
environment variables `TWITTER_CONSUMER_KEY`, `TWITTER_CONSUMER_SECRET`,
`TWITTER_ACCESS_TOKEN_KEY`, `TWITTER_ACCESS_TOKEN_SECRET`.

# Local

## Configuring foreman

KarmaNotes runs on Heroku as a webapp and thus makes use of a Procfie. While
not strictly necessary, KarmaWorld can use the same basic Procfile which is
convenient and consistent.

To use the Procfile locally, we recommend using `foreman`. To install `foreman`
and other Heroku tools, install the
[Heroku toolbelt](https://toolbelt.heroku.com/).

Ensure environment variables are available to `foreman` by copying
`.env.example` to `.env` and update those variables as appropriate for your
local system.

## pdf2htmlEX

This project uses [pdf2htmlEX](https://github.com/coolwanglu/pdf2htmlEX) as
a dependency. pdf2htmlEX is used to convert uploaded PDF notes into HTML. It
needs to be installed on the same system that KarmaWorld is running on.

### using their source

See their instructions at
[https://github.com/coolwanglu/pdf2htmlEX/wiki/Building](https://github.com/coolwanglu/pdf2htmlEX/wiki/Building).

Make sure to [patch](https://github.com/FinalsClub/pdf2htmlEX/commit/3c19f6abd8d59d1b58cf254b7160b332b3f5b517)
the source code to expose two variables.

### using our fork

You can use FinalsClub's [outdated version of pdf2htmlEX](https://github.com/FinalsClub/pdf2htmlEX).
See their installation instructions above, but don't worry about patching.

### using their PPA

You can use [their upstream PPA](https://launchpad.net/~coolwanglu/+archive/ubuntu/pdf2htmlex).

        apt-add-repository ppa:coolwanglu/pdf2htmlex
        apt-get update
        apt-get install pdf2htmlex

Then patch the javascript on your system by running this code in the shell.

        cat >> `dpkg -L pdf2htmlex | grep pdf2htmlEX.js` <<PDF2HTMLEXHACK
        Viewer.prototype['rescale'] = Viewer.prototype.rescale;
        Viewer.prototype['scroll_to'] = Viewer.prototype.scroll_to;
        PDF2HTMLEXHACK

## Install

  1. `virtualenv venv`
  1. `source venv/bin/activate`
  1. `pip install -r requirements.txt`
    * on Debian systems, some packages are required for pip to succeed:
    * `apt-get install python-dev libpython-dev python-psycopg2 libmemcached-dev libffi-dev libssl-dev postgresql-server-dev-X.Y`
  1. `pip install -r requirements-dev.txt`

## Configuration

Make sure [External Service Dependencies](#external_service_dependencies) are
satisfied. This includes running a local database and RabbitMQ instance as
desired.

  1. configure `.env` as per [instructions](#external_service_dependencies)
  1. `foreman run python manage.py syncdb --migrate --noinput`
  1. `foreman run python manage.py createsuperuser`
  1. `foreman run python manage.py fetch_usde_csv ./schools.csv`
  1. `foreman run python manage.py import_usde_csv ./schools.csv`
  1. `foreman run python manage.py sanitize_usde_schools`

* `fetch_usde_csv` downloads school records and stores them to `./schools.csv`. This file name
     and location is arbitrary. As long as the same file is passed into `import_usde_csv` for
     reading, everything should be fine.

* `fetching_usde_csv` requires `7zip` to be installed for processing compressed
     archives. On Debian-based systems, this entails `apt-get install p7zip-full`

## Run

Make sure you are inside your virtual environment (`source venv/bin/activate`).

If the code has changed or this is the first run, make sure any modified static
files get compressed with `foreman run python manage.py compress`. Static files
then need to be uploaded correctly with `foreman run python manage.py
collectstatic`.

Run `foreman start`.  `foreman` will load the `.env` file and manage running all
processes in a way that is similar to that of Heroku. This allows better
consistency with local, staging, and production deployments.

To run web-only, but no celery or beat, run `foreman start web` to specify
strictly the web worker.

Press ctrl-C to kill foreman. Foreman will run Django's runserver command.
If you wish to have more control over how this is done, you can do
`foreman run python manage.py runserver <options>`. For running any other
`manage.py` commands, you should also precede them with `foreman run` like just shown.
This simply ensures that the environment variables from `.env` are present.

# Heroku Install

KarmaNotes runs on Heroku as a webapp. This section addresses what was done
for KarmaNotes so that other implementations of KarmaWorld can be run on
Heroku.

Before anything else, download the [Heroku toolbelt](https://toolbelt.heroku.com/).

To run KarmaWorld on Heroku, do `heroku create` and `git push heroku master` as typical
for a Heroku application. Set your the variable `BUILDPACK_URL` to
`https://github.com/FinalsClub/heroku-buildpack-karmanotes` to use a buildpack
designed to support KarmaNotes.

You will need to import the US Department of Education's list of accredited schools.
   1. Fetch USDE schools with
      `heroku run python manage.py fetch_usde_csv ./schools.csv`
   1. Upload the schools into the database with
      `heroku run python /manage.py import_usde_csv ./schools.csv`
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
