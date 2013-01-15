"""Management utilities."""

import os
from contextlib import contextmanager as _contextmanager

from fabric.contrib.console import confirm
from fabric.api import abort, cd, env, local, prefix, run, settings, task


########## GLOBALS
env.proj_repo = 'git@github.com:FinalsClub/karmaworld.git'
env.virtualenv = 'venv-kw'
env.activate = 'workon %s' % env.virtualenv
########## END GLOBALS


########## HELPERS
def cont(cmd, message):
    """Given a command, ``cmd``, and a message, ``message``, allow a user to
    either continue or break execution if errors occur while executing ``cmd``.

    :param str cmd: The command to execute on the local system.
    :param str message: The message to display to the user on failure.

    .. note::
        ``message`` should be phrased in the form of a question, as if ``cmd``'s
        execution fails, we'll ask the user to press 'y' or 'n' to continue or
        cancel exeuction, respectively.

    Usage::

        cont('heroku run ...', "Couldn't complete %s. Continue anyway?" % cmd)
    """
    with settings(warn_only=True):
        result = local(cmd, capture=True)

    if message and result.failed and not confirm(message):
        abort('Stopped execution per user request.')


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
def beta():
    """
    Beta connection information
    """
    env.user = 'djkarma'
    env.hosts = ['beta.karmanotes.org']
    env.proj_root = '/var/www/karmaworld'
    env.proj_dir = os.path.join(env.proj_root, 'karmaworld')


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
    """Run a syncdb."""
    local('%(run)s syncdb --noinput' % env)


@task
def migrate(app=None):
    """Apply one (or more) migrations. If no app is specified, fabric will
    attempt to run a site-wide migration.

    :param str app: Django app name to migrate.
    """
    if app:
        local('%s migrate %s --noinput' % (env.run, app))
    else:
        local('%(run)s migrate --noinput' % env)
########## END DATABASE MANAGEMENT


########## FILE MANAGEMENT
@task
def collectstatic():
    """Collect all static files, and copy them to S3 for production usage."""
    local('%(run)s collectstatic --noinput' % env)
########## END FILE MANAGEMENT


########## COMMANDS

def make_virtualenv():
    """
    Creates a virtualenv on the remote host
    """
    run('mkvirtualenv %s' % env.virtualenv)


def update_reqs():
    """
    Makes sure all packages listed in requirements are installed
    """
    with _virtualenv():
        with cd(env.proj_dir):
            run('pip install -r requirements/production.pip')


def clone():
    """
    Clones the project from the central repository
    """
    run('git clone %s %s' % (env.proj_repo, env.proj_dir))


def update_code():
    """
    Pulls the latest changes from the central repository
    """
    with cd(env.proj_dir):
        run('git pull')


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
