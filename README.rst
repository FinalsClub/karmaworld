==========
KarmaWorld
==========
:Description: A django application for sharing and uploading class notes.
:Copyright: FinalsClub, a 501c3 non-profit organization
:License: GPLv3 except where otherwise noted
:Contact: info@karmanotes.org

v3.0 of the karmanotes.org website from the FinalsClub Foundation




Purpose
=======

KarmaNotes is an online database of college lecture notes.  KarmaNotes empowers college students to participate in the free exchange of knowledge. 

Docs
====

TODO: see `./docs/`
TODO: Put docs on [RTFD](https://readthedocs.org/)


Install
=======
If you're starting to work on this project and you need it setup on your local
machine, follow the steps below.

1. Make sure you have installed ``git``, the ``PostgreSQL`` server, client and
   development files, ``Python`` including the development files, ``Fabric``,
   ``pip``, ``virtualenv`` and ``virtualenvwrapper``.

2. Clone the project from the central repo::

        git clone git@github.com:FinalsClub/karmaworld.git

Note that you have to have your SSH keys setup on GitHub to use this URL. If
you don't, you can use the HTTP URL:
``https://github.com/FinalsClub/karmaworld.git``.

3. Create a database and optionally a username and put them in the
   ``DATABASES`` setting in a ``local.py`` file that you'll place in
   ``karmaworld/settings/``.

4. Make sure that you're in the root of the project that you just cloned and
   run

        fab here first_deploy

This will make a virtualenv, install the development dependencies and create
the database tables.

5. Now you can run ``./manage.py runserver`` and visit the site in the browser.

Thanks
======

* KarmaNotes.org is a project of the FinalsClub Foundation with generous funding from the William and Flora Hewlett Foundation

* Also thanks to [rdegges](https://github.com/rdegges/django-skel) for the django-skel template
