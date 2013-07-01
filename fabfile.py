
""" Karmaworld Fabric management script
    Finals Club (c) 2013"""

import os

from fabric.api import cd, env, lcd, prefix, run, task, local, settings
from fabvenv import virtualenv

######### GLOBAL
env.proj_repo = 'git@github.com:FinalsClub/karmaworld.git'


######## Define host(s)
@task
def here():
    """
    Connection information for the local machine
    """

    # This is required for the same reason as above
    env.proj_dir = os.getcwd()
    env.proj_root = os.path.dirname(env.proj_dir)
    env.cd = lcd
    env.reqs = 'reqs/dev.txt'
    env.confs = 'confs/stag/'
    env.branch = 'beta'
    env.run = virtenv_exec

@task
def prod():
    """
    Connection Information for production machine
    """

    env.user = 'djkarma'
    env.hosts = ['beta.karmanotes.org']
    env.proj_root = '/var/www/karmaworld'
    env.proj_dir = '/var/www/karmaworld'
    env.reqs = 'reqs/prod.txt'
    env.confs = 'confs/beta/'
    env.branch = 'beta'
    env.run = virtenv_exec
    env.gunicorn_addr = '127.0.0.1:8000'

######## Run Commands in Virutal Environment
def virtenv_exec(command):
        """
	Execute command in Virtualenv
	"""

        with virtualenv('%s/%s' % (env.proj_dir, env.branch)):
                run('%s' % (command))



######## Sync database
@task
def syncdb():
	"""
	Sync Database
	"""

	env.run('%s/manage.py syncdb --noinput --migrate' % env.proj_dir )


####### Collect Static Files
@task
def collect_static():
	"""
	Collect static files (if AWS config. present, push to S3
	"""

	env.run('%s/manage.py collectstatic --noinput' % env.proj_dir )	

####### Run Dev Server
@task
def dev_server():
	"""
	Runs the built-in django webserver
	"""

	env.run('%s/manage.py runserver' % env.proj_dir )	

####### Create Virtual Environment
@task
def make_virtualenv():
	"""
	Create our Virtualenv in $SRC_ROOT
	"""

	run('virtualenv %s/%s' % (env.proj_dir, env.branch))
	env.run('pip install -r %s/reqs/dev.txt' % env.proj_dir )

@task
def start_gunicorn():
    """
    Starts the gunicorn process
    """
    env.run('%s/manage.py run_gunicorn -b %s -u %s -p var/run/gunicorn.pid' % (env.proj_root, env.gunicorn_addr, env.user)

@task
def update_reqs():
	env.run('pip install -r reqs/dev.txt')


@task
def update_code():
	env.run('cd %s; git pull' % env.proj_dir)

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


@task
def User():
	env.run('whoami')
