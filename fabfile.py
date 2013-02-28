"""Management utilities."""

import os
from contextlib import contextmanager as _contextmanager

from fabric.api import cd, env, prefix, run, task, local


########## GLOBALS
env.proj_repo = 'git@github.com:FinalsClub/karmaworld.git'
env.virtualenv = 'venv-kw'
env.activate = 'workon %s' % env.virtualenv

# Using this env var to be able to specify the function
# used to run the commands. By default it's `run`, which
# runs commands remotely, but in the `here` task we set
# env.run to `local` to run commands locally.
env.run = run
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
def here():
    """
    Connection information for the local machine
    """
    env.proj_dir = os.getcwd()
    env.proj_root = os.path.dirname(env.proj_dir)
    env.run = local
    env.reqs = 'reqs/dev.txt'
    env.confs = 'confs/dev/'
    env.branch = 'master'


@task
def beta():
    """
    Beta connection information
    """
    env.user = 'djkarma'
    env.hosts = ['beta.karmanotes.org']
    env.proj_root = '/var/www/karmaworld'
    env.proj_dir = os.path.join(env.proj_root, 'karmaworld')
    env.reqs = 'reqs/prod.txt'
    env.confs = 'confs/beta/'
    env.branch = 'beta'


@task
def prod():
    """
    Production connection information
    """
    env.user = 'djkarma'
    env.hosts = ['karmanotes.org']
    env.proj_root = '/var/www/karmaworld'
    env.proj_dir = os.path.join(env.proj_root, 'karmaworld')
    env.reqs = 'reqs/prod.txt'
    env.confs = 'confs/prod/'
    env.branch = 'master'
########## END ENVIRONMENTS


########## DATABASE MANAGEMENT
@task
def syncdb():
    """Runs syncdb (along with any pending South migrations)"""
    env.run('python manage.py syncdb --noinput --migrate')
########## END DATABASE MANAGEMENT


########## FILE MANAGEMENT
@task
def manage_static():
    """
    Collects, compresses and uploads static files.
    """
    collect_static()
    compress_static()
    upload_static()


@task
def collect_static():
    """Collect all static files, and copy them to S3 for production usage."""
    env.run('python manage.py collectstatic --noinput')


@task
def compress_static():
    """
    Compresses the static files.
    """
    pass


@task
def upload_static():
    """
    Uploads the static files to the specified host.
    """
    pass
########## END FILE MANAGEMENT


########## COMMANDS
@task
def make_virtualenv():
    """
    Creates a virtualenv on the remote host
    """
    env.run('mkvirtualenv %s' % env.virtualenv)


@task
def update_reqs():
    """
    Makes sure all packages listed in requirements are installed
    """
    with _virtualenv():
        with cd(env.proj_dir):
            env.run('pip install -r %s' % env.reqs)


@task
def clone():
    """
    Clones the project from the central repository
    """
    env.run('git clone %s %s' % (env.proj_repo, env.proj_dir))


@task
def update_code():
    """
    Pulls changes from the central repo and checks out the right branch
    """
    with cd(env.proj_dir):
        env.run('git pull && git checkout %s' % env.branch)


@task
def start_supervisord():
    """
    Starts supervisord
    """
    with _virtualenv():
        config_file = os.path.join(env.confs, 'supervisord.conf')
        env.run('supervisord -c %s' % config_file)


@task
def stop_supervisord():
    """
    Restarts supervisord
    """
    with _virtualenv():
        config_file = os.path.join(env.confs, 'supervisord.conf')
        env.run('supervisorctl -c %s shutdown' % config_file)


@task
def restart_supervisord():
    """
    Restarts supervisord
    """
    stop_supervisord()
    start_supervisord()


def supervisorctl(action, process):
    """
    Takes as arguments the name of the process as is
    defined in supervisord.conf and the action that should
    be performed on it: start|stop|restart.
    """
    supervisor_conf = os.path.join(env.confs, 'supervisord.conf')
    env.run('supervisorctl -c %s %s %s' % (supervisor_conf, action, process))


@task
def start_celeryd():
    """
    Starts the celeryd process
    """
    supervisorctl('start', 'celeryd')


@task
def stop_celeryd():
    """
    Stops the celeryd process
    """
    supervisorctl('stop', 'celeryd')


@task
def restart_celery():
    """
    Restarts the celeryd process
    """
    supervisorctl('restart', 'celeryd')


@task
def start_gunicorn():
    """
    Starts the gunicorn process
    """
    supervisorctl('start', 'gunicorn')


@task
def stop_gunicorn():
    """
    Stops the gunicorn process
    """
    supervisorctl('stop', 'gunicorn')


@task
def restart_gunicorn():
    """
    Restarts the gunicorn process
    """
    supervisorctl('restart', 'gunicorn')


@task
def deploy():
    """
    Deploys the latest changes
    """
    update_code()
    update_reqs()
    syncdb()
    manage_static()
    restart_supervisord()
########## END COMMANDS
