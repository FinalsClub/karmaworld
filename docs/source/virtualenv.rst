Virtualenv
==========

`Virtualenv <http://www.virtualenv.org/en/latest/index.html>`_ is a tool for managing python requirements.
We use it to manage development and deployment requirements when we have multiple python projects on the same host.

This isn't strictly required for the project, but we recommend it.
You can install virtualenv with 

    $ pip install virtualenv

Then create an environment to contain karmaworld packages:

    virtualenv venv

And then activate the virtual enviroment with:

    source ./venv/bin/activate

Run this activate script before trying to run ./manage.py commands or other server commands.
