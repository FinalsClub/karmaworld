Layout
======

Here is the rough karmaworld repo layout::

    .
    ├── fabfile.py
    ├── gunicorn.py.ini
    ├── manage.py
    ├── Procfile
    ├── reqs
    │   ├── common.txt
    │   ├── dev.txt
    │   └── prod.txt
    ├── requirements.txt
    ├── karmaworld
    │   ├── apps
    │   │   ├── __init__.py
    │   │   ├── courses
    │   │   │   ├── models.py
    │   │   │   └── …
    │   │   ├── notes
    │   │   │   ├── models.py
    │   │   │   └── …
    │   ├── __init__.py
    │   ├── libs
    │   │   └── __init__.py
    │   ├── settings
    │   │   ├── common.py
    │   │   ├── dev.py
    │   │   ├── __init__.py
    │   │   └── prod.py
    │   ├── templates
    │   │   ├── 404.html
    │   │   └── 500.html
    │   └── urls.py
    └── wsgi.py


``fabfile.py`` is a utility script (written using `Fabric
<http://docs.fabfile.org/en/1.4.2/index.html>`_) that adds some helpful
shortcut commands. It can automatically bootstrap a Heroku app for you, and a
number of other useful things. You can run ``fab --list`` from the command line
to see its usage.

``gunicorn.py.ini`` is our `gunicorn <http://gunicorn.org/>`_ web server
configuration file. It is optimized for large scale sites, and should work well
in any environment.

``manage.py`` is our default Django management script. It uses the `dev.py` settings file, so we will have to override this in production

``Procfile`` is our Heroku process file--which tells Heroku what our three
types of services are: ``web``, ``scheduler``, and ``worker``. To learn more
about this, see `Heroku's Procfile documentation
<https://devcenter.heroku.com/articles/procfile>`_.

``reqs`` is a directory which contains all of our pip requirement files, broken
into categories by the environment in which they're used. The ``common.txt``
file contains all of our 'shared' requirements, the ``dev.txt`` file contains
all of our local development requirements, and the ``prod.txt`` file contains
our production requirements. This modular approach is taken to make development
as flexible (and intuitive) as possible.

``requirements.txt`` is a Heroku specific file which tells Heroku to install
our production requirements *only*.

``karmaworld`` is the Django project site. Everything inside this directory is
considered the actual Django code.

``karmaworld/apps`` is the directory meant to hold all of our local Django
applications.

``karmaworld/libs`` is a directory meant to hold all of your local Django
libraries--code which doesn't really fit into 'applications'. This usually
includes stuff like templatetags that are used in various place, or other
helpful utility functions.

``karmaworld/settings`` is a directory which holds all of your Django settings files!
Much like our pip requirements, there is a settings file for each environment:
``dev.py``, ``prod.py``, and ``common.py`` (shared settings).

``karmaworld/templates`` is a directory that holds all your Django templates.

``karmaworld/urls.py`` is your standard Django urlconf.

``wsgi.py`` is your standard Django wsgi configuration file. Our webserver
uses this to figure things out :)


.. image:: _static/yeah.png
