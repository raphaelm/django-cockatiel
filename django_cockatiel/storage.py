import copy
import hashlib
import random
import urllib.parse

import requests
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation, ImproperlyConfigured
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.encoding import filepath_to_uri
from django.utils.six.moves.urllib.parse import urljoin

from .conf import DEFAULT


class CockatielFile(File):
    def __init__(self, response, mode='rb'):
        self.response = response
        self.file = response.raw
        self.mode = mode

    def read(self, num_bytes=None):
        b = self.file.read(num_bytes)
        if 'b' not in self.mode:
            return b.decode(self.response.encoding or 'utf-8')
        return b

    def write(self, content):
        raise NotImplemented()


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

    def _get_url(self, node, name):
        return urllib.parse.urljoin(node, name)

    def _retry(self, func):
        nodes = list(self.conf.get('STORAGE_NODES'))
        random.shuffle(nodes)
        try:
            node = nodes.pop(random.randrange(0, len(nodes)))
            return func(node)
        except:
            if not nodes:
                raise

    def _open(self, name, mode='rb'):
        def get(node):
            resp = requests.get(self._get_url(node, name), stream=True)
            resp.raise_for_status()
            return resp

        resp = self._retry(get)
        return CockatielFile(resp, mode)

    def _save(self, name, content):
        if not hasattr(content, 'seek'):
            raise SuspiciousFileOperation('The django-cockatiel backend can only deal with '
                                          'files that support seeking.')
        content.seek(0)
        sha1 = hashlib.sha1()
        while True:
            chunk = content.read(1024)
            if not chunk:
                break
            sha1.update(chunk)

        content.seek(0)

        def put(node):
            resp = requests.put(self._get_url(node, name), data=content, headers={
                'X-Content-SHA1': sha1.hexdigest()
            }, allow_redirects=False)
            resp.raise_for_status()
            return resp

        resp = self._retry(put)
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
        def delete(node):
            resp = requests.delete(self._get_url(node, name))
            if resp.status_code == 404:
                return resp  # That is fine
            resp.raise_for_status()
            return resp

        self._retry(delete)

    def exists(self, name):
        # All names are "available"
        return False

    def url(self, name):
        if self.conf.get('PUBLIC_URL') is None:
            raise ValueError("This file is not accessible via a URL.")
        return urljoin(self.conf.get('PUBLIC_URL'), filepath_to_uri(name))
