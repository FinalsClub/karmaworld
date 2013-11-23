
""" Karmaworld Fabric management script
    Finals Club (c) 2013"""

import os

from fabric.api import cd, env, lcd, prefix, run, task, local, settings
from fabric.contrib import files

######### GLOBAL
env.proj_repo = 'git@github.com:FinalsClub/karmaworld.git'
env.repo_root = '~/karmaworld'
env.proj_root = '/var/www/karmaworld'
env.branch = 'prod'
env.code_root = '{0}/{1}-code'.format(env.proj_root, env.branch)

######## Define host(s)
def here():
    """
    Connection information for the local machine
    """
    def _custom_local(command):
        prefixed_command = '/bin/bash -l -i -c "%s"' % command
        return local(prefixed_command)

    # This is required for the same reason as above
    env.proj_root = '/var/www/karmaworld'
    env.cd = lcd
    env.reqs = 'reqs/dev.txt'
    env.confs = 'confs/beta'
    env.branch = 'beta'



####### Define production host
@task
def prod():
    """
    Connection Information for production machine
    """

    env.user = 'djkarma'
    env.hosts = ['karmanotes.org']
    env.proj_root = '/var/www/karmaworld'
    env.reqs = 'reqs/prod.txt'
    env.confs = 'confs/prod/'
    env.branch = 'beta'
    env.gunicorn_addr = '127.0.0.1:8000'

####### Define beta host
@task
def beta():
    """
    Connection Information for beta machine
    """

    env.user = 'djkarma'
    env.hosts = ['beta.karmanotes.org']
    env.proj_root = '/var/www/karmaworld'
    env.reqs = 'reqs/prod.txt'
    env.confs = 'confs/prod/'
    env.branch = 'beta'

######## Run Commands in Virutal Environment
def virtenv_exec(command):
    """
    Execute command in Virtualenv
    """

    path = os.path.sep.join( (env.proj_root, env.branch) )
    with prefix('source {0}/bin/activate'.format(path)):
        run(command)

######## Sync database
@task
def syncdb():
    """
    Sync Database
    """
    virtenv_exec('{0}/manage.py syncdb --migrate'.format(env.code_root))


####### Collect Static Files
@task
def collect_static():
	"""
	Collect static files (if AWS config. present, push to S3)
	"""

	virtenv_exec('%s/manage.py collectstatic --noinput' % env.proj_root )	

####### Run Dev Server
@task
def dev_server():
	"""
	Runs the built-in django webserver
	"""

	virtenv_exec('%s/manage.py runserver' % env.proj_root)	

####### Create Virtual Environment
@task
def make_virtualenv():
	"""
	Create our Virtualenv in env.proj_root
	"""

        path = os.path.sep.join( (env.proj_root, env.branch) )
        if not files.exists(path):
            run('virtualenv {0}'.format(path))
        if not files.exists(env.code_root):
            run('ln -s {0} {1}'.format(env.repo_root, env.code_root))

@task
def start_supervisord():
    """
    Starts supervisord
    """
    virtenv_exec('supervisord -c {0}/confs/{1}/supervisord.conf'.format(env.code_root, env.branch))


@task
def stop_supervisord():
    """
    Restarts supervisord
    """
    config_file = '/var/www/karmaworld/confs/prod/supervisord.conf'
    virtenv_exec('supervisorctl -c %s shutdown' % config_file)


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
    supervisor_conf = '/var/www/karmaworld/confs/prod/supervisord.conf'
    virtenv_exec('supervisorctl -c %s %s %s' % (supervisor_conf, action, process))


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


####### Update Requirements
@task
def update_reqs():
    virtenv_exec('pip install -r {0}/reqs/{1}.txt'.format(env.repo_root, env.branch))

####### Pull new code
@task
def update_code():
    virtenv_exec('cd %s; git pull' % env.proj_root )

def backup():
    """
    Create backup using bup
    """
    pass

@task
def first_deploy():
    """
    Sets up and deploys the project for the first time.
    """
    make_virtualenv()
    update_reqs()
    syncdb()
    manage_static()
    start_supervisord()


@task
def deploy():
    """
    Deploys the latest changes
    """
    update_code()
    update_reqs()
    syncdb()
    collect_static()
    restart_supervisord()
########## END COMMANDS
