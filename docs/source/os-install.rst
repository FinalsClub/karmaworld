OS installation
===============

In production, we use Ubuntu 12.04 server.  Here we should document what system plackes should be installed via `apt` and how they may be configured.


RabbitMQ
--------

RabbitMQ is a task-queue server written in erlang.
It is installed on ubuntu via:

    sudo apt-get install rabbitmq-server

RabbitMQ does not require configuration, celery will connect to it automatically.

