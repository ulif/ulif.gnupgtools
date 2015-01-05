#
# Helpers for testing
#
import os
import shutil
import tempfile


def doctest_setup():
    """Setup env for complex doctests.
    """
    pass


def doctest_teardown():
    """Clean up env after complex doctests.
    """
    pass


class FakeGnuPGHomeTestCase(object):
    """A test case that provides a fake GnuPG home.
    """

    gnupg_home = None

    def create_empty_gpg_home(self):
        self._old_gnupg_home = os.getenv('GNUPGHOME', None)
        self.gnupg_home = tempfile.mkdtemp()
        os.environ['GNUPGHOME'] = self.gnupg_home
        return os.environ['GNUPGHOME']

    def cleanup_gpg_home(self):
        if self.gnupg_home is None:
            return
        if self._old_gnupg_home is None:
            del os.environ['GNUPGHOME']
        else:
            os.environ['GNUPGHOME'] = self._old_gnupg_home
        if not os.path.isdir(self.gnupg_home):
            return
        shutil.rmtree(self.gnupg_home)
