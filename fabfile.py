
""" Karmaworld Fabric management script
    Finals Club (c) 2013"""

import os
import ConfigParser

from fabric.api import cd, env, lcd, prefix, run, sudo, task, local, settings
from fabric.contrib import files

######### GLOBAL
env.group = 'www-data'
env.proj_repo = 'git@github.com:FinalsClub/karmaworld.git'
env.repo_root = '~/karmaworld' # transient setting for VMs only
env.proj_root = '/var/www/karmaworld'
env.branch = 'prod' # only used for supervisor conf two lines below. cleanup?
env.code_root = env.proj_root
env.env_root = env.proj_root
env.supervisor_conf = '{0}/confs/{1}/supervisord.conf'.format(env.code_root, env.branch)
env.usde_csv = '{0}/confs/acceditation.csv'.format(env.code_root)

env.use_ssh_config = True


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
    Restarts supervisord, also making sure to load in new config data.
    """
    virtenv_exec('supervisorctl -c {0} update'.format(env.supervisor_conf))
    virtenv_exec('supervisorctl -c {0} restart all'.format(env.supervisor_conf))


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
          sudo('chown {0}:{1} {2}'.format(env.local_user, env.group, filepath))

@task
def check_secrets():
    """
    Ensure secret files exist for syncdb to run.
    """

    secrets_path = env.code_root + '/karmaworld/secret'
    secrets_files = ('filepicker.py', 'static_s3.py', 'db_settings.py', 'drive.py', 'client_secrets.json', 'drive.p12')

    errors = []
    for sfile in secrets_files:
        ffile = os.path.sep.join((secrets_path,sfile))
        if not files.exists(ffile):
            errors.append('{0} missing. Please add and try again.'.format(ffile))
    if errors:
        raise Exception('\n'.join(errors))

@task
def fetch_usde():
    """
    Download USDE accreditation school CSV.
    """
    virtenv_exec('{0}/manage.py fetch_usde_csv {1}'.format(env.code_root, env.usde_csv))

@task
def import_usde():
    """
    Import accreditation school CSV into the database and scrub it.
    """
    virtenv_exec('{0}/manage.py import_usde_csv {1}'.format(env.code_root, env.usde_csv))
    virtenv_exec('{0}/manage.py sanitize_usde_schools'.format(env.code_root))

@task
def install_pdf2htmlEX():
    """
    # Some things we need:
    sudo apt-get install cmake libpng-dev libjpeg-dev libgtk2.0-dev pkg-config libfontconfig1-dev autoconf libtool

    # Ubuntu 12.04 comes with a version of poppler that is too
    # old, so compile our own
    wget http://poppler.freedesktop.org/poppler-0.24.4.tar.xz
    tar xf poppler-0.24.4.tar.gz
    ./configure --prefix=/usr --enable-xpdf-headers
    make
    sudo make install

    # Ubuntu 12.04 comes with a version of fontforge that is too
    # old, so compile our own
    git clone https://github.com/fontforge/fontforge.git
    ./autogen.sh
    ./configure --prefix=/usr
    make
    sudo make install

    # Compile pdf2htmlEX
    wget https://github.com/coolwanglu/pdf2htmlEX/archive/v0.10.tar.gz
    tar xf x0.10.tar.gz
    cd pdf2htmlEX
    cmake .
    make
    sudo make install
    """
    print "not implemented yet!"

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
    collect_static()
    fetch_usde()
    import_usde()
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
