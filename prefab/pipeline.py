from __future__ import absolute_import

import itertools
import functools
from collections import OrderedDict

from fabric.api import env, execute as _execute, puts
from fabric.state import output
from fabtools.vagrant import ssh_config

from prefab.environ import gather


def _vagrant(name=''):
    config = ssh_config(name)

    settings = {
        'user': config['User'],
        'key_filename': config['IdentityFile'].strip('"'),
        'forward_agent': config.get('ForwardAgent', 'no') == 'yes',
        'disable_known_hosts': True,
    }

    env.update(settings)


def execute(task):
    """
    Perform vagrant checking before executing task
    """
    # setup env from a VM name
    if env.get('vagrant', False):
        # Use KeyError to fail - ip_map is necessary
        ip_map = env['vagrant']['ip_map']
        _vagrant(ip_map[env.host])

    _execute(task)


def once(f):
    """
    Decorator ensuring that the wrapped function is executed once per host
    during fabric's execution. The return value is cached for further
    invocations. This is distinctly different from ``fabric.api.runs_once``, as
    ``runs_once`` ensures that the decorated function is only executed once per
    ``fab`` program execution.

    .. note:: Results are stored in a ``host_cache`` attribute.

    .. note:: ``once`` *probably* works with parallel task execution.
    """
    # # optional argument handling
    # if f is None:
    #     return functools.partial(once, optional_arg=optional_arg)

    host_cache = {}
    host_format = "%(host)s:%(port)s"

    def has_executed(host):
        return host in host_cache

    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # we want to cache per host:port, for forwarding purposes
        host = host_format % env
        if not has_executed(host):
            host_cache[host] = f(*args, **kwargs)
        else:
            if output.debug:
                puts("pipeline: '%s' task already executed!" % f.__name__)
                puts('pipeline: Cached results: %s' % host_cache[host])
        return host_cache[host]

    decorated.host_cache = host_cache
    decorated.host_format = host_format
    decorated.has_executed = has_executed
    decorated.once = True
    return decorated


def requires(*prereqs):
    """
    """

    # the actual decorator
    def decorator(f):

        @functools.wraps(f)
        def decorated(*args, **kwargs):
            for req in prereqs:
                execute(req)

            return f(*args, **kwargs)

        decorated.requires = prereqs
        return decorated

    return decorator


def environ(*names):
    def decorator(f):

        @functools.wraps(f)
        def decorated(*args, **kwargs):
            # environment variables *should* be gathered in `process`, but
            # this is necessary in case the task is executed on its own.
            for name in names:
                gather(name)
            return f(*args, **kwargs)

        decorated.envvars = names
        return decorated

    return decorator


def process(*tasks):
    """
    A convenience function for executing tasks within a pipeline. Pre-determines
    and linearizes execution order of tasks to produce slightly nicer output.

    It is not required to ``process`` tasks. Fabric's ``execute`` will function
    properly.

    """
    names = [s.__name__ for s in tasks]
    tasks = _expand_tasks(tasks)

    # print task execution order
    puts('pipeline: processing tasks %s' % names)
    puts('pipeline: execution order')
    for task in tasks:
        puts('pipeline:   - %s' % task.__name__)
    print

    # process envvars gathering upfront
    envvars = [getattr(task, 'envvars', []) for task in tasks]  # get lists of vars for tasks
    envvars = itertools.chain(*envvars)  # chain lists into a single list
    envvars = list(OrderedDict.fromkeys(envvars))  # remove duplicates from list

    # front load environment variable gathering.
    if envvars:
        puts('pipeline: gathering environment variables')
        for name in envvars:
            puts('pipeline: \'%s\' environment' % name)
            gather(name)
        print

    # execute tasks
    for task in tasks:
        puts('pipeline: executing \'%s\'' % task.__name__)
        execute(task)


def _expand_tasks(tasks):
    expanded_tasks = []

    for task in tasks:
        if hasattr(task, 'requires'):
            for sub_task in _expand_tasks(task.requires):
                if sub_task not in expanded_tasks:
                    expanded_tasks.append(sub_task)
        if task not in expanded_tasks:
            expanded_tasks.append(task)

    return expanded_tasks
