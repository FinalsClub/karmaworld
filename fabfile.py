
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

####### Supervisord
@task
def start_supervisord():
	"""
	Starts Supervisord
	"""
	config_file = '%s/confs/prod/supervisord.conf' % (env.proj_dir)
	env.run('supervisord -c %s' % config_file)

@task
def stop_supervisord():
    	"""
    	Stops supervisord
    	"""
	
	config_file = '%s/confs/prod/supervisord.conf' % (env.proj_dir)
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
	config_file = '%s/confs/prod/supervisord.conf' % (env.proj_dir)
	env.run('supervisorctl -c %s %s %s' % (config_file, action, process))

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
    manage_static()
    restart_supervisord()


@task
def User():
	env.run('whoami')
