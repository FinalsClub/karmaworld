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
API keys, credentials, and other information that you must provide to KarmaNotes
as environment variables. The best way to persist these environment variables is
by using a `.env` file. Copy `.env.example` to `.env` and populate the fields as
required.

### Heroku
This project has chosen to use [Heroku](www.heroku.com) to host the Django and
celery software. While not a hard requirement, the more up-to-date parts of this
documentation will operate assuming Heroku is in use.

See README.heroku for more information.

### Amazon S3
The instructions for creating an [S3](http://aws.amazon.com/s3/) bucket may be
[found on Amazon.](http://docs.aws.amazon.com/AmazonS3/latest/gsg/CreatingABucket.html)

Two, separate buckets will be needed in production: one for static file hosting
and one as a communication bus with Filepicker.

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
Filepicker section below.

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
KarmaNotes uses IndexDen to create a searchable index of all the notes in the
system. Create an free IndexDen account at
[their homepage](http://indexden.com/). You will be given a private URL that
accesses your IndexDen account. This URL is visible on your dashboard (you
might need to scroll down).

Set the `INDEXDEN_PRIVATE_URL` environment variable to your private URL.

Set the `INDEXDEN_INDEX` environment variable to the name of the index you want
to use for KarmaNotes. The index will be created automatically when KarmaNotes
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

### SSL Certificate

If you wish to host your system publicly, you'll need an SSL certificate
signed by a proper authority.

Follow [Heroku's SSL setup](https://devcenter.heroku.com/articles/ssl-endpoint)
to get SSL running on your server.

You may set the `SSL_REDIRECT` environment variable to `true` to make KarmaNotes
redirect insecure connections to secure ones.

# Local Install

KarmaNotes is a Heroku application. Download the [Heroku toolbelt](https://toolbelt.heroku.com/).

Before your running it for the first time, there are
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

To run KarmaNotes locally, make sure you are inside your
virtual environment (`source venv/bin/activate`) and run `foreman start`.
Press ctrl-C to kill foreman. Foreman will run Django's runserver command.
If you wish to have more control over how this is done, you can do
`foreman run python manage.py runserver <options>`. For running any other
`manage.py` commands, you should also precede them with `foreman run` like just shown.
This simply ensures that the environment variables from `.env` are present.

# Heroku Install

KarmaNotes is a Heroku application. Download the [Heroku toolbelt](https://toolbelt.heroku.com/).

To run KarmaNotes on Heroku, do `heroku create` and `git push heroku master` as typical
for a Heroku application. Set your the variable `BUILDPACK_URL` to
`https://github.com/charlesconnell/heroku-buildpack-karmanotes` to use a buildpack designed
to support KarmaNotes.

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
