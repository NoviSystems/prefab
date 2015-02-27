
from fabric.api import env, task
from fabric.contrib import django

import json


def load_from_file(environ, path='environ.json'):
    with open(path) as configfile:
        conf = json.load(configfile)[environ]

        django.settings_module(conf['django_settings'])

        fabenv = conf.pop('env', {})

        # for now, also use env to store other global state
        env.update(conf)

        # and finally update with the env dict
        env.update(fabenv)


def load_from_remote(environ, uri):
    pass


def load(environ):
    loader = load_from_file
    if hasattr(env, 'preferred_environ_loader'):
        loader = env.preferred_environ_loader

    loader(environ)


@task
def environ(environ):
    """
    Setup the environment that is being worked on.  [prod, stag, test, default]
    """
    env.environ = environ
    load(environ)
