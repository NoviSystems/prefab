
from fabric.api import env
from fabric.contrib import django

import json
import os

DEFAULTS = {
    "django_settings": os.environ.get("DJANGO_SETTINGS_MODULE", ""),
    "upload_settings": False,
}


def load_from_file(environ, path='environ.json'):
    with open(path) as configfile:
        conf = json.load(configfile)[environ]
        defaults = DEFAULTS.copy()

        django.settings_module(conf['django_settings'])

        if conf.get('vagrant_environ', False):
            home = os.path.expanduser('~')
            key_path = '.vagrant.d/insecure_private_key'

            defaults.update({
                'user': 'vagrant',
                'key_filename': os.path.join(home, key_path),
            })

        fabenv = conf.pop('env', {})

        # for now, also use env to store other global state
        env.update(defaults)
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
