
""" Karmaworld Fabric management script
    Finals Club (c) 2013"""

import os
import ConfigParser

from fabric.api import cd, env, lcd, prefix, run, sudo, task, local, settings
from fabric.contrib import files

######### GLOBAL
env.user = 'vagrant'
env.group = 'vagrant'
env.proj_repo = 'git@github.com:FinalsClub/karmaworld.git'
env.repo_root = '~/karmaworld'
env.proj_root = '/var/www/karmaworld'
env.branch = 'prod'
env.code_root = env.proj_root
env.env_root = env.proj_root
env.supervisor_conf = '{0}/confs/{1}/supervisord.conf'.format(env.code_root, env.branch)

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
def virtenv_path():
    """
    Builds the virtualenv path.
    """
    # not much here now, but maybe useful later.
    return env.env_root

def virtenv_exec(command):
    """
    Execute command in Virtualenv
    """

    path = virtenv_path()
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

	virtenv_exec('%s/manage.py collectstatic --noinput' % env.code_root )	

####### Run Dev Server
@task
def dev_server():
	"""
	Runs the built-in django webserver
	"""

	virtenv_exec('%s/manage.py runserver' % env.code_root)	

####### Create Virtual Environment

@task
def link_code():
    """
    Link the karmaworld repo into the appropriate production location
    """
    if not files.exists(env.code_root):
        run('ln -s {0} {1}'.format(env.repo_root, env.code_root))

@task
def make_virtualenv():
    """
    Create our Virtualenv
    """
    run('virtualenv {0}'.format(virtenv_path()))

@task
def start_supervisord():
    """
    Starts supervisord
    """
    virtenv_exec('supervisord -c {0}'.format(env.supervisor_conf))


@task
def stop_supervisord():
    """
    Restarts supervisord
    """
    virtenv_exec('supervisorctl -c {0} shutdown'.format(env.supervisor_conf))


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
    virtenv_exec('supervisorctl -c {0} {1} {2}'.format(env.supervisor_conf, action, process))


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
def file_setup():
    """
    Deploy expected files and directories from non-apt system services.
    """
    ini_parser = ConfigParser.SafeConfigParser()
    if not ini_parser.read(env.supervisor_conf):
      raise Exception("Could not parse INI file {0}".format(env.supervisor_conf))
    for section, option in (('supervisord','logfile'),
                            ('supervisord','pidfile'),
                            ('unix_http_server','file'),
                            ('program:celeryd','stdout_logfile')):
      filepath = ini_parser.get(section, option)
      # generate file's directory structure if needed
      run('mkdir -p {0}'.format(os.path.split(filepath)[0]))
      # touch a file and change ownership if needed
      if 'log' in option and not files.exists(filepath):
          sudo('touch {0}'.format(filepath))
          sudo('chown {0}:{1} {2}'.format(env.user, env.group, filepath))

@task
def check_secrets():
    """
    Ensure secret files exist for syncdb to run.
    """

    secrets_path = env.code_root + '/karmaworld/secret'
    secrets_files = ('filepicker.py', 'static_s3.py', 'db_settings.py')

    errors = []
    for sfile in secrets_files:
        ffile = os.path.sep.join((secrets_path,sfile))
        if not files.exists(ffile):
            errors.append('{0} missing. Please add and try again.'.format(ffile))
    if errors:
        raise Exception('\n'.join(errors))

@task
def first_deploy():
    """
    Sets up and deploys the project for the first time.
    """
    link_code()
    make_virtualenv()
    file_setup()
    check_secrets()
    update_reqs()
    syncdb()
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
