
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

######## Run Commands in Virutal Environment
def virtenv_exec(command):
        with virtualenv('%s/%s' % (env.proj_dir, env.branch)):
                run('%s' % (command))



######## Sync database
@task
def syncdb():
	env.run('%s/manage.py syncdb --noinput --migrate' % env.proj_dir )


####### Collect Static Files
@task
def collect_static():
	env.run('%s/manage.py collectstatic --noinput' % env.proj_dir )	

####### Run Dev Server
@task
def dev_server():
	env.run('%s/manage.py runserver' % env.proj_dir )	

####### Create Virtual Environment
@task
def make_virtualenv():
	run('virtualenv %s/%s' % (env.proj_dir, env.branch))
	env.run('pip install -r %s/reqs/dev.txt' % env.proj_dir )

####### Supervisord
@task
def start_supervisord():
	config_file = '%s/%ssupervisord.conf' % (env.proj_dir,env.confs)
	env.run('supervisord -c %s' % config_file)

