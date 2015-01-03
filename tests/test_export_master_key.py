import os
import shutil
import tempfile
import unittest

class TestGPGExportMasterKeyTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.workdir = os.path.join(self.temp_dir, 'work')
        self.gnupg_home = os.path.join(self.temp_dir, 'gnupghome')
        self.old_env_gnupg_home = os.getenv('GNUPGHOME', None)
        os.environ['GNUPGHOME'] = self.gnupg_home

    def tearDown(self):
        if self.old_env_gnupg_home is None:
            del os.environ['GNUPGHOME']
        else:
            os.environ['GNUPGHOME'] = self.old_env_gnupg_home
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_foo(self):
        assert 1 == 0
