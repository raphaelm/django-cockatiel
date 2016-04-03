import os
import socket
import sys
import tempfile
import time
from multiprocessing import Process

import pytest
from cockatiel.server import run

import settings

sys.path.insert(0, os.path.abspath('..'))

port = os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')


def waitfor(func, timeout=10, interval=0.5):
    started = time.time()
    while True:
        try:
            func()
            break
        except:
            if time.time() - started >= timeout:
                raise
            else:
                time.sleep(interval)


# Choose a free port
port = os.environ.get('COCKATIEL_TEST_PORT')
if not port:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    os.environ.setdefault('COCKATIEL_TEST_PORT', str(port))
else:
    port = int(port)

tmpdir = tempfile.TemporaryDirectory()
qdir = tempfile.TemporaryDirectory()
args = ('-p', str(port), '--storage', tmpdir.name, '--queue', qdir.name)
p = Process(target=run, args=(args,))
p.start()

settings.COCKATIEL_STORAGE_OPTIONS['STORAGE_NODES'].append(
    'http://127.0.0.1:{}'.format(port)
)

def up():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', port))
    s.close()


waitfor(up, interval=.05)

exc = pytest.main(sys.argv[1:])

p.terminate()

sys.exit(exc)