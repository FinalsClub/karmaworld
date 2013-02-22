"""Management utilities."""

import os
from contextlib import contextmanager as _contextmanager

from fabric.api import cd, env, local, prefix, run, settings, task


########## GLOBALS
env.proj_repo = 'git@github.com:FinalsClub/karmaworld.git'
env.virtualenv = 'venv-kw'
env.activate = 'workon %s' % env.virtualenv
env.run = './manage.py'
########## END GLOBALS


########## HELPERS
@_contextmanager
def _virtualenv():
    """
    Changes to the proj_dir and activates the virtualenv
    """
    with cd(env.proj_dir):
        with prefix(env.activate):
            yield

########## END HELPERS

########## ENVIRONMENTS
@task
def beta():
    """
    Beta connection information
    """
    env.user = 'djkarma'
    env.hosts = ['beta.karmanotes.org']
    env.proj_root = '/var/www/karmaworld'
    env.proj_dir = os.path.join(env.proj_root, 'karmaworld')


@task
def prod():
    """
    Production connection information
    """
    env.user = 'djkarma'
    env.hosts = ['karmanotes.org']
    env.proj_root = '/var/www/karmaworld'
    env.proj_dir = os.path.join(env.proj_root, 'karmaworld')
########## END ENVIRONMENTS


########## DATABASE MANAGEMENT
@task
def syncdb():
    """Runs syncdb (along with any pending South migrations)"""
    run('python manage.py syncdb --noinput --migrate')
########## END DATABASE MANAGEMENT


########## FILE MANAGEMENT
@task
def collectstatic():
    """Collect all static files, and copy them to S3 for production usage."""
    local('%(run)s collectstatic --noinput' % env)
########## END FILE MANAGEMENT


########## COMMANDS

@task
def make_virtualenv():
    """
    Creates a virtualenv on the remote host
    """
    run('mkvirtualenv %s' % env.virtualenv)


@task
def update_reqs():
    """
    Makes sure all packages listed in requirements are installed
    """
    with _virtualenv():
        with cd(env.proj_dir):
            run('pip install -r requirements/production.pip')


@task
def clone():
    """
    Clones the project from the central repository
    """
    run('git clone %s %s' % (env.proj_repo, env.proj_dir))


@task
def update_code():
    """
    Pulls the latest changes from the central repository
    """
    with cd(env.proj_dir):
        run('git pull')


@task
def deploy():
    """
    Creates or updates the project, runs migrations, installs dependencies.
    """
    first_deploy = False
    with settings(warn_only=True):
        if run('test -d %s' % env.proj_dir).failed:
            # first_deploy var is for initial deploy information
            first_deploy = True
            clone()
        if run('test -d $WORKON_HOME/%s' % env.virtualenv).failed:
            make_virtualenv()

    update_code()
    update_reqs()
    syncdb()
    #TODO: run gunicorn
    #restart_uwsgi()
########## END COMMANDS
