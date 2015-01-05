# Tests for ulif.gnupg.testing
import os
import shutil
import tempfile
import unittest
from ulif.gnupgtools.testing import (
    FakeGnuPGHomeTestCase,
    )


class FakeGnuPGHomeTestCaseTests(unittest.TestCase):

    def setUp(self):
        self.old_home = os.getenv('GNUPGHOME', None)
        os.environ['GNUPGHOME'] = 'MY-FAKE-HOME'

    def tearDown(self):
        new_home = os.getenv('GNUPGHOME', None)
        if (self.old_home is None) and (new_home is not None):
            del os.environ['GNUPGHOME']
        elif self.old_home is not None:
            os.environ['GNUPGHOME'] = self.old_home
        if new_home is None:
            return
        if os.path.isdir(new_home) and (self.old_home != new_home):
            shutil.rmtree(new_home)

    def test_create_new_home(self):
        # the test case can create a new home
        old_gpghome = os.getenv('GNUPGHOME', None)
        os.environ['GNUPGHOME'] = 'MY-FAKE-HOME'
        case = FakeGnuPGHomeTestCase()
        result = case.create_empty_gpg_home()
        assert result != 'MY-FAKE-HOME'
        assert old_gpghome != result
        assert os.getenv('GNUPGHOME', None) == result
        assert os.path.isdir(result)

    def test_cleanup_gpg_home(self):
        # we can cleanup a fake GPG home
        fake_home = tempfile.mkdtemp()
        os.environ['GNUPGHOME'] = fake_home
        case = FakeGnuPGHomeTestCase()
        case._old_gnupg_home = 'MY-FAKE-HOME'
        case.gnupg_home = fake_home
        case.cleanup_gpg_home()
        assert os.getenv('GNUPGHOME', None) == 'MY-FAKE-HOME'
        assert not os.path.exists(fake_home)

    def test_cleanup_gpg_home_no_home(self):
        # if the current home is none, there is nothing to delete
        case = FakeGnuPGHomeTestCase()
        case.gnupg_home = None
        case._old_gnupg_home = 'MY-OLD-FAKE-HOME'
        os.environ['GNUPGHOME'] = 'MY-FAKE-HOME'
        case.cleanup_gpg_home()
        assert os.getenv('GNUPGHOME', None) == 'MY-OLD-FAKE-HOME'

    def test_cleanup_gpg_home_no_old_home(self):
        # if there were no old home set, we will handle it correctly
        case = FakeGnuPGHomeTestCase()
        case._old_gnupg_home = None
        case.gnupg_home = None
        os.environ['GNUPGHOME'] = 'MY-FAKE-HOME'
        case.cleanup_gpg_home()
        assert 'GNUPGHOME' not in os.environ
