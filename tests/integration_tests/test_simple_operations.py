from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def test_put_and_read():
    f = ContentFile(b'This is test content')
    filename = default_storage.save('foobar.txt', f)
    assert filename
    with default_storage.open(filename) as f:
        assert f.read() == b'This is test content'
