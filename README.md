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
this software may require considerable overhaul.

### Filepicker
This software uses [Filepicker.io](https://www.inkfilepicker.com/) for uploading
files. This requires an account with Filepicker.

Filepicker requires an additional third party file hosting site where it may
send uploaded files. For this project, we have used Amazon S3.

Filepicker will provide an API key. This is needed by the software.

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
Create a file at karmaworld/secret/indexden.py, and enter your private URL, and the name
of the index you want KarmaNotes to use. The index will be created automatically when
KarmaNotes is run if it doesn't already exist. For example,
```
PRIVATE_URL = 'http://:secretsecret@secret.api.indexden.com'
INDEX = 'karmanotes_something_something'
```

### Google Drive
This software uses [Google Drive](https://developers.google.com/drive/) to
convert documents to and from various file formats.

A Google Drive service account with access to the Google Drive is required. Thismay be done with a Google Apps account with administrative privileges, or ask
your business sysadmin.

These are the instructions to create a Google Drive service account:
https://developers.google.com/drive/delegation

When completed, you'll have a file called `client_secrets.json` and a p12 file
which is the key to access the service account. Both are needed by the software.

### Twitter

Twitter is used to post updates about new courses. Access to the Twitter API
will be required for this task.

If this Twitter feature is desired, the consumer key and secret as well as the
access token key and secret are needed by the software.

If the required files are not found, then no errors will occur.

To set this up, create a new Twitter application at https://dev.twitter.com/apps/new.
Make sure this application has read/write access. Generate an access token. Go to your
OAuth settings, and grab the "Consumer key", "Consumer secret", "Access token", and
"Access token secret".

Create a file at karmaworld/secret/twitter.py, and enter these tokens. For example,
```
CONSUMER_KEY = '???'
CONSUMER_SECRET = '???'
ACCESS_TOKEN_KEY = '???'
ACCESS_TOKEN_SECRET = '???'
```

### SSL Certificate

If you wish to host your system publicly, you'll need an SSL certificate
signed by a proper authority.

If you are working on local system for development, a self signed certificate
will suffice. There are plenty of resources available for learning how to
create one, so that will not be detailed here. Note that the Vagrant file will
automatically generated a self signed certificate within the virtual machine.

The certificate should be installed using nginx.

# Development Install

If you need to setup the project for development, it is highly recommend that
you grab create a development virtual machine or (if available) grab one that
has already been created for your site.

The *host machine* is the system which runs e.g. VirtualBox, while the
*virtual machine* refers to the system running inside e.g. VirtualBox. 

## Creating a Virtual Machine by hand

Create a virtual machine with your favorite VM software. Configure the virtual
machine for production with the steps shown in the [Production Install](#production-install) section.

## Creating a Virtual Machine with Vagrant

Vagrant supports a variety of virtual machine software and there is additional
support for Vagrant to deploy to a wider variety. However, for these
instructions, it is assumed Vagrant will be deployed to VirtualBox.

1. Configure external dependencies on the host machine:
   * Under `{project_root}/karmaworld/secret/`:
        1. Copy files with the example extension to the corresponding filename
          without the example extension (e.g.
          `cp filepicker.py.example filepicker.py`)
        1. Modify those files, but ignore `db_settings.py` (Vagrant takes care of that one)
        1. Copy the Google Drive service account p12 file to `drive.p12`
           (this filename and location may be changed in `drive.py`)
        1. Ensure `*.py` in `secret/` are never added to the git repo.
           (.gitignore should help warn against taking this action)

1. Install [VirtualBox](http://www.virtualbox.org/)

1. Install [vagrant](http://www.vagrantup.com/) 1.3 or higher

1. Use Vagrant to create the virtual machine.
   * While in `cd {project_root}`, type `vagrant up`

1. Connect to the virtual machine with `vagrant ssh`

Note:
Port 443 of the virtual machine will be configured as port 6659 on the host
system. While on the host system, fire up your favorite browser and point it at
`https://localhost:6659/`. This connects to your host system on port 6659, which
forwards to your virtual machine's web site using SSL.

Port 80 of the virtual machine will be configured as port 16659 on the host
system. While on the host system, fire up your favorite browser and point it at
`http://localhost:16659/`. This connects to your host system on port 16659,
which forwards to your virtual machine's web site using plain text.

## Completing the Virtual Machine with Fabric

*Notice* Fabric might not run properly if you presently in a virtualenv.
`deactivate` prior to running fab commands.

### From the Host Machine

If Fabric is available on the host machine, you should be able to run Fabric
commands directly on the host machine, pointed at the virtual machine. If
Fabric is not available on the Host Machine, see the next section.

To setup the host machine properly, see the section about
[accessing the VM via fabric](#accessing-the-vm-via-fabric) and then return to
this section.

Assuming those steps were followed with the alias, the following instructions
should complete the virtual machine setup:

1. `cd {project_root}` on the host machine.

1. type `vmfab first_deploy`.

### From within the Virtual Machine

If Fabric is not available on the host machine, or just for funsies, you may
run the Fabric commands within the virtual machine.

1. Connect to the virtual machine with `vagrant ssh`.

1. On the virtual machine, type `cd karmanotes` to get into the code
   repository.

1. In the code repo of the VM, type `fab -H 127.0.0.1 first_deploy`

   During this process, you will be queried to create a Django site admin.
   Provide information. You will be asked to remove duplicate schools. Respond
   with yes.

# Production Install

These steps are taken care of by automatic utilities. Vagrant performs the
first subsection of these instructions and Fabric performs the second
subsection. These instructions are detailed here for good measure, but should
not generally be needed.

1. Ensure the following are installed:
   * `git`
   * `7zip` (for unzipping US Department of Education files)
   * `PostgreSQL` (server and client)
   * `nginx`
   * `libxslt` and `libxml2` (used by some Python libraries)
   * `RabbitMQ` (server)
   * `memcached`
   * `Python`
   * `PIP`
   * `virtualenv`
   * `virtualenvwrapper` (might not be needed anymore)
   * `pdf2htmlEX`

   On a Debian system supporting Apt, this can be done with:
```
    sudo apt-get install python-pip postgresql python-virtualenv nginx \
    virtualenvwrapper git libxml2-dev p7zip-full \
    postgresql-server-dev-9.1 libxslt1-dev \
    libmemcached-dev python-dev rabbitmq-server \
    cmake libpng-dev libjpeg-dev libgtk2.0-dev \
    pkg-config libfontconfig1-dev autoconf libtool

    wget http://poppler.freedesktop.org/poppler-0.24.4.tar.xz
    tar xf poppler-0.24.4.tar.xz
    cd poppler-0.24.4
    ./configure --prefix=/usr --enable-xpdf-headers
    make
    sudo make install
    cd ~/

    git clone https://github.com/fontforge/fontforge.git
    cd fontforge
    ./bootstrap
    ./configure --prefix=/usr
    make
    sudo make install
    cd ~/

    git clone https://github.com/charlesconnell/pdf2htmlEX.git
    cd pdf2htmlEX
    ./configure --prefix=/usr
    cmake .
    make
    sudo make install
```

1. Generate a PostgreSQL database and a role with read/write permissions.
   * For Debian, these instructions are helpful: https://wiki.debian.org/PostgreSql

1. Modify configuration files.
   * There are settings in `{project_root}/karmaworld/settings/prod.py`
       * Most of the setting should work fine by default.
   * There are additional configuration options for external dependencies
     under `{project_root}/karmaworld/secret/`.
        1. Copy files with the example extension to the corresponding filename
          without the example extension (e.g.
          `cp filepicker.py.example filepicker.py`)
        1. Modify those files.
           * Ensure `PROD_DB_USERNAME`, `PROD_DB_PASSWORD`, and `PROD_DB_NAME`
             inside `db_settings.py` match the role, password, and database
             generated in the previous step.
        1. Copy the Google Drive service account p12 file to `drive.p12`
           (this filename and location may be changed in `drive.py`)
        1. Ensure `*.py` in `secret/` are never added to the git repo.
           (.gitignore should help warn against taking this action)

1. Make sure that /var/www exists, is owned by the www-data group, and that
   the desired user is a member of the www-data group.

1. Configure nginx with a `proxy_pass` to port 8000 (or whatever port gunicorn
   will be running the site on) and any virtual hosting that is desired.
   Here is an example server file to put into `/etc/nginx/sites-available/`

        server {
            listen 80;
            server_name localhost;
            return 301 https://$host$request_uri;
        }

        server {
            listen 443;
            ssl on;
            server_name localhost;
            client_max_body_size 20M;
        
            location / {
                # pass traffic through to gunicorn
                proxy_pass http://127.0.0.1:8000;
                # pass HTTP(S) status through to Django
                proxy_set_header X-Forwarded-SSL $https;
                proxy_set_header X-Forwarded-Protocol $scheme;
                proxy_set_header X-Forwarded-Proto $scheme;
                # pass nginx site back to Django
                proxy_set_header Host $http_host;
            }
        }

1. Configure the system to start supervisor on boot. An init script for
   supervisor is in the repo at `{project_root}/karmaworld/confs/supervisor`.
   `update-rc.d supervisor defaults` is the Debian command to load the init
   script into the correct directories.

1. Make sure `{project_root)/var/log` and `{project_root}/var/run` exist and
   may be written to, or else put the desired logging and run file paths into
   `{project_root}/confs/prod/supervisord.conf`

1. Create a virtualenv under `/var/www/karmaworld/venv`

1. Change into the virtualenv with `. /var/www/karmaworld/venv/bin/activate`.
   Within the virtualenv:

    1. Update the Python depenencies with `pip -i {project_root}/reqs/prod.txt`
        * If you want debugging on a production-like system:
            1. run `pip -i {project_root}/reqs/vmdev.txt`
            1. change `{project_root}/manage.py` to point at `vmdev.py`
               instead of `prod.py`
            1. ensure firefox is installed on the system (such as by
               `sudo apt-get install firefox`)
    
    1. Setup the database with `python {project_root}/manage.py syncdb --migrate`

    1. Collect static resources and put them in the static hosting location with
       `python {project_root}/manage.py collect_static`

1. The database needs to be populated with schools. A list of accredited schools
   may be found on the US Department of Education website:
   http://ope.ed.gov/accreditation/GetDownloadFile.aspx

   Alternatively, use the built-in scripts while in the virtualenv:

   1. Fetch USDE schools with
      `python {project_root}/manage.py fetch_usde_csv ./schools.csv`

   1. Upload the schools into the database with
      `python {project_root}/manage.py import_usde _csv ./schools.csv`

   1. Clean up redundant information with
      `python {project_root}/manage.py sanitize_usde_schools`

1. Startup `supervisor`, which will run `celery` and `gunicorn`. This may be
   done from within the virtualenv by typing
   `python {project_root}/manage.py start_supervisord`

1. If everything went well, gunicorn should be running the website on port 8000
   and nginx should be serving gunicorn on port 80.

# Update a deployed system

Once code has been updated, the running web service will need to be updated
to stay in sync with the code.

## Fabric

Run the `deploy` fab command. For example:
`fab -H 127.0.0.1 deploy`

## By Hand

1. pull code in from the repo with `git pull`
1. If any Python requirements have changed, install/upgrade them:
    `pip install -r --upgrade reqs/prod.txt`
1. If the database has changed, update the database with:
    `python manage.py syncdb --migrate`
1. If any static files have changed, synchornize them with;
    `python manage.py collectstatic`
1. Django will probably need a restart.
    * For a dev system, ctrl-c the running process and restart it.
    * For a production system, there are two options.
        * `python manage.py restart_supervisord` if far reaching changes
          have been made (that might effect celery, beat, etc)
        * `python manage.py restart_gunicorn` if only minor Django changes
          have been made
        * If you are uncertain, best bet is to restart supervisord.

# Accessing the Vagrant Virtual Machine

## Accessing the VM via Fabric
If you have Fabric on the host machine, you can configure your host machine
to run Fabric against the virtual machine.

You will need to setup the host machine with the proper SSH credentials to
access the virtual machine. This is done by running `vagrant ssh-config` from
`{project_root}` and copying the results into your SSH configuration file
(usually found at `~/.ssh/config`).

The VM will, by default, route its SSH connection through localhost port 2222
on the host machine and the base user with be vagrant. Point Fabric there when
running fab commands from `{project_root}`. So the command will look like this:

        fab -H 127.0.0.1 --port=2222 -u vagrant <commands>

In unix, it might be convenient to create and use an alias like so:

        alias vmfab='fab -H 127.0.0.1 --port=2222 -u vagrant'
        vmfab <commands>

Removing a unix alias is done with `unalias`.

## Connecting to the VM via SSH
If you have installed a virtual machine using `vagrant up`, you can connect
to it by running `vagrant ssh` from `{project_root}`.

## Connecting to the development website on the VM
To access the website running on the VM, point your browser at
http://localhost:6659/ using your host computer.

Port 6659 on your local machine is set to forward to the VM's port 80.

Fun fact: 6659 was chosen because of OM (sanskrit) and KW (KarmaWorld) on a
phone: 66 59.

## Updating the VM code repository
Once connected to the virtual machine by SSH, you will see `karmaworld` in
the home directory. That is the `{project_root}` in the virtual machine.

`cd karmaworld` and then use `git fetch; git merge` and/or `git pull origin` as
desired.

The virtual machine's code repository is set to use your host machine's
local repository as the origin. So if you make changes locally and commit them,
without pushing them anywhere, your VM can pull those changes in for testing.

This may seem like duplication. It is. The duplication allows your host machine
to maintain git credentials and manage repository access control so that your
virtual machine doesn't need sensitive information. Your virtual machine simply
pulls from the local repository on your local file system without needing
credentials, etc.

## Deleting the Virtual Machine
If you want to start a fresh virtual machine or simply remove the virtual
machine from your hard drive, Vagrant has a command for that. While in 
`{project_root}` of the host system, type `vagrant destroy` and confirm with
`y`. This will remove the VM from your hard drive.

If you wanted a fresh VM, the next step is to run `vagrant up`, which will
start a brand new VM (since the old one is gone).

## Other Vagrant commands
Please see [vagrant documentation](http://docs.vagrantup.com/v2/cli/index.html)
for more information on how to use the vagrant CLI to manage your development
VM.

# Django Database management

## South

We have setup Django to use
[south](http://south.aeracode.org/wiki/QuickStartGuide) for migrations. When
changing models, it is important to run
`python {project_root}/manage.py schemamigration` which will create a migration
 to reflect the model changes into the database. These changes can be pulled
into the database with `python {project_root}/manage.py migrate`.

Sometimes the database already has a migration performed on it, but that
information wasn't told to south. There are subtleties to the process which
require looking at the south docs. As a tip, start by looking at the `--fake`
flag.

# Assets from Third Parties

A number of assets have been added to the repository which come from external
sources. It would be difficult to keep a complete list in this README and keep
it up to date. Software which originally came from outside parties can
generally be found in `{project_root}/karmaworld/assets`.

Additionally, all third party Python projects (downloaded and installed with
pip) are listed in these files:

* `{project_root}/reqs/common.txt`
* `{project_root}/reqs/dev.txt`
* `{project_root}/reqs/prod.txt`
* `{project_root}/reqs/vmdev.txt` (just a combo of dev.txt and prod.txt)

# Thanks

* KarmaNotes.org is a project of the FinalsClub Foundation with generous funding from the William and Flora Hewlett Foundation

* Also thanks to [rdegges](https://github.com/rdegges/django-skel) for the django-skel template
