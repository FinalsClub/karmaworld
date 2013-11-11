# KarmaWorld
__Description__: A django application for sharing and uploading class notes.

__Copyright__: FinalsClub, a 501c3 non-profit organization

__License__: GPLv3 except where otherwise noted

__Contact__: info@karmanotes.org

v3.0 of the karmanotes.org website from the FinalsClub Foundation




# Purpose

KarmaNotes is an online database of college lecture notes.  KarmaNotes empowers college students to participate in the free exchange of knowledge. 

# Pre-Installation

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

# Development Install

If you need to setup the project for development, it is highly recommend that
you grab an existing development virtual machine for create one yourself, and
then configure the virtual machine for production with the steps shown in the
next section. Instructions for creating a virtual machine follow:

1. Install [VirtualBox](http://www.virtualbox.com/)

1. Install [vagrant](http://www.vagrantup.com/)

1. Use Vagrant to create the virtual machine.
    * While in `cd {project_root}`, type `vagrant up`

# Production Install

If you're starting to work on this project and you need it setup for production,
follow the steps below.

1. Ensure the following are installed:
   * `git`
   * `PostgreSQL` (server and client)
   * `Python`
   * `PIP`
   * `virtualenv` and `virtualenvwrapper`

1. Generate a PostgreSQL database and a role with read/write permissions.
   * For Debian, these instructions are helpful: https://wiki.debian.org/PostgreSql

1. Modify configuration files.
   * There are settings in `{project_root}/karmaworld/settings/dev.py`
   * There are additional configuration options for external dependencies
     under `{project_root}/karmaworld/secret/`.
       * Copy files with the example extension to the corresponding filename
         without the example extension (e.g.
         `cp filepicker.py.example filepicker.py`) 
       * Modify those files.
           * Ensure `PROD_DB_USERNAME`, `PROD_DB_PASSWORD`, and `PROD_DB_NAME`
             inside `db_settings.py` match the role, password, and database
             generated in the previous step.
       * Ensure *.py in `secret/` are never added to the git repo. (.gitignore
         should help warn against taking this action)

1. Make sure that you're in the root of the project that you just cloned and
   run

        fab here first_deploy

   This will make a virtualenv, install the development dependencies and create
   the database tables.

1. Now you can run ``./manage.py runserver`` and visit the site in the browser.

# Accessing the Vagrant Virtual Machine

## Connecting to the VM via SSH
If you have installed a virtual machine using `vagrant up`, you can connect
to it by running `vagrant ssh` from `{project_root}`.

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

## Other Vagrant commands
Please see [vagrant documentation](http://docs.vagrantup.com/v2/cli/index.html)
for more information on how to use the vagrant CLI to manage your development
VM.

Thanks
======

* KarmaNotes.org is a project of the FinalsClub Foundation with generous funding from the William and Flora Hewlett Foundation

* Also thanks to [rdegges](https://github.com/rdegges/django-skel) for the django-skel template
