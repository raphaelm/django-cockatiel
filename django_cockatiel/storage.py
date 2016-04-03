import copy
import hashlib
import random
import urllib.parse

import requests
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation, ImproperlyConfigured
from django.core.files import File
from django.core.files.storage import Storage

from .conf import DEFAULT


class CockatielFile(File):
    def __init__(self, response):
        self.file = response.raw
        self._is_dirty = False

    def read(self, num_bytes=None):
        return self.file.read(num_bytes)

    def write(self, content):
        raise NotImplemented()

    def close(self):
        self.file.close()


class CockatielStorage(Storage):
    def __init__(self, options=None):
        conf = copy.copy(DEFAULT)
        if hasattr(settings, 'COCKATIEL_STORAGE_OPTIONS'):
            conf.update(settings.COCKATIEL_STORAGE_OPTIONS)
        if options:
            conf.update(options)
        self.conf = conf
        if not self.conf.get('STORAGE_NODES'):
            raise ImproperlyConfigured('You did not configure any cockatiel storage nodes.')

    def _get_url(self, name):
        node = random.choice(self.conf.get('STORAGE_NODES'))
        return urllib.parse.urljoin(node, name)

    def _open(self, name, mode='r'):
        resp = requests.get(self._get_url(name), stream=True)
        resp.raise_for_status()
        return CockatielFile(resp)

    def _save(self, name, content):
        sha1 = hashlib.sha1()
        while True:
            chunk = content.read(1024)
            if not chunk:
                break
            sha1.update(chunk)

        content.seek(0)
        resp = requests.put(self._get_url(name), data=content, headers={
            'X-Content-SHA1': sha1.hexdigest()
        })
        resp.raise_for_status()
        loc = resp.headers['Location']
        if loc.startswith('/'):
            loc = loc[1:]
        return loc

    def get_available_name(self, name, max_length=None):
        if max_length and len(name) + 41 > max_length:
            raise SuspiciousFileOperation(
                'Storage can not find an available filename for "%s". '
                'Please make sure that the corresponding file field '
                'allows sufficient "max_length".' % name
            )
        return name

    def delete(self, name):
        resp = requests.put(self._get_url(name))
        if resp.status_code == 404:
            return  # That is fine
        resp.raise_for_status()

    def exists(self, name):
        # All names are "available"
        return False

    def url(self, name):
        pass
