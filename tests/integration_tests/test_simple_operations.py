import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from requests import HTTPError


def test_put_and_read():
    f = ContentFile(b'This is test content')
    filename = default_storage.save('foobar.txt', f)
    assert filename
    with default_storage.open(filename) as f:
        assert f.read() == b'This is test content'


def test_put_twice():
    f = ContentFile(b'This is test content')
    filename1 = default_storage.save('twice.txt', f)
    filename2 = default_storage.save('twice.txt', f)
    assert filename1 == filename2
    with default_storage.open(filename1) as f:
        assert f.read() == b'This is test content'


def test_put_and_read_text_mode():
    f = ContentFile(b'This is test content')
    filename = default_storage.save('textmode.txt', f)
    assert filename
    with default_storage.open(filename, 'r') as f:
        assert f.read() == 'This is test content'


def test_put_and_delete():
    f = ContentFile(b'This is test content')
    filename = default_storage.save('deletion.txt', f)
    assert filename
    with default_storage.open(filename, 'r') as f:
        assert f.read() == 'This is test content'
    default_storage.delete(filename)
    with pytest.raises(HTTPError):
        default_storage.open(filename)


def test_url_disabled():
    f = ContentFile(b'This is test content')
    filename = default_storage.save('url.txt', f)
    with pytest.raises(ValueError):
        default_storage.url(filename)


def test_url():
    default_storage.conf['PUBLIC_URL'] = '/media/'
    f = ContentFile(b'This is test content')
    filename = default_storage.save('url.txt', f)
    assert filename
    assert default_storage.url(filename) == '/media/{}'.format(filename)
    default_storage.conf['PUBLIC_URL'] = None
