'''
Convenience module for console prompts. All functions default to returning
partials so that they can be invoked lazily.
'''
from functools import partial, wraps
from getpass import getpass

from fabric import api
from fabric.contrib import console


__all__ = ('prompt', 'confirm', 'secure_prompt')


@wraps(api.prompt)
def prompt(*args, **kwargs):
    lazy = kwargs.pop('lazy', True)

    if not lazy:
        return api.prompt(*args, **kwargs)
    return partial(api.prompt, *args, **kwargs)


@wraps(console.confirm)
def confirm(*args, **kwargs):
    lazy = kwargs.pop('lazy', True)

    if not lazy:
        return console.confirm(*args, **kwargs)
    return partial(console.confirm, *args, **kwargs)


def secure_prompt(text, lazy=True):
    text = text.strip() + ' '

    if not lazy:
        return getpass(text)
    return partial(getpass, text)
