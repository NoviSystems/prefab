
from fabric.contrib import django
from fabric.api import env, task

from prefab.environ import fabenv

__all__ = [
    'settings', 'environ', 'shell',
]


# turn fabric helper method into an actual task.
settings = task(name='settings')(django.settings_module)


@task
def environ(environ):
    """
    Setup the environment that is being worked on.  [prod, stag, test, default]
    """
    env.environ = environ
    fabenv(environ)


@task
def shell():
    """
    Runs a Python interactive interpreter.

    This code is modified from django's ``shell`` manangement command.

    Usage::

        $ fab -H <hostname> shell

    """
    from fabric.api import settings
    import code
    # Set up a dictionary to serve as the environment for the shell, so
    # that tab completion works on objects that are imported at runtime.
    # See ticket 5082.
    imported_objects = {}
    try:  # Try activating rlcompleter, because it's handy.
        import readline
    except ImportError:
        pass
    else:
        # We don't have to wrap the following import in a 'try', because
        # we already know 'readline' was imported successfully.
        import rlcompleter
        readline.set_completer(rlcompleter.Completer(imported_objects).complete)
        readline.parse_and_bind("tab:complete")

    with settings(warn_only=True):
        code.interact(local=imported_objects)
