django-cockatiel
================

[![Build Status](https://travis-ci.org/raphaelm/django-cockatiel.svg?branch=master)](https://travis-ci.org/raphaelm/django-cockatiel)

This is a django storage backend that makes use of the cockatiel distributed
file storage. Please read the [cockatiel documentation](https://cockatiel.readthedocs.org/)
if you are unsure about what this is.

Requirements
------------

* Django 1.8 or 1.9
* Python 3.4 or newer

Installation
------------

To install django-cockatiel, you can simply run:

    pip install django-cockatiel

If you want to use it as your primary media file storage, you need to
add some configuration to your ``settings.py`` file. First of all, you
need to set it as your default storage:

    DEFAULT_FILE_STORAGE = 'django_cockatiel.CockatielStorage'

Next, you need to configure django-cockatiel itself. Currently, the
following configuration options are available:

* ``PUBLIC_URL``: The public URL that the files can be reached at. This
  could be the public address of one of your nodes or the address of a
  lode balancer of some kind.

* ``STORAGE_NODES``: The list of storage nodes that should be used to
  store files. This should be a list of URLs of cockatiel instances.

Example:

    COCKATIEL_STORAGE_OPTIONS = {
        'PUBLIC_URL': '/media/',
        'STORAGE_NODES': [
            'http://10.1.2.3:8012'
        ]
    }

