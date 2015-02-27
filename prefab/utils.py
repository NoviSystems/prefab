
from fabric.api import env


def host_roles(host):
    """
    Builds a list of roles that the host is associated with.
    """
    roles = []

    for role, conf in env.roledefs.items():
        # dict style roledef
        if isinstance(conf, dict):
            conf = conf['hosts']

        if host in conf:
            roles.append(role)

    return roles


def role_hosts(role=None):
    """
    Gets the list of hosts that are associated with the role. If no role is
    specified, all hosts are compiled into a single set.
    """
    hosts = set()

    roles = env.roledefs.keys() if role is None else [role]

    for role in roles:
        conf = env.roledefs[role]

        # dict style roledef
        if isinstance(conf, dict):
            conf = conf['hosts']

        if callable(conf):
            conf = conf()

        hosts.update(conf)

    return hosts
