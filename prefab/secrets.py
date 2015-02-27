
from fabric.api import env


if 'secrets' not in env:
    env.secrets = {}


def register(name, defaults):
    """
    """
    env.secrets[name] = defaults


def context(name, **kwargs):
    """
    """
    secrets = env.secrets
    secrets[name].update(kwargs)

    for key, value in secrets[name].items():
        if callable(value):
            secrets[name][key] = value()

    return secrets[name]
