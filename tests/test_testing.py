# Tests for ulif.gnupg.testing
import os
import shutil
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
        elif self.old_home is None:
            os.environ['GNUPGHOME'] = self.old_gpg_home
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
