import unittest
import re
from mediaserver_processor.helpers import FileWatcher


class TestConfigurationMethods(unittest.TestCase):
    def setUp(self):
        self.watcher = FileWatcher('/')

    def test_include_pattern(self):
        self.assertEquals(self.watcher.include_pattern, re.compile(r"^[._]"))

    def test_should_watch_dir(self):
        self.assertFalse(self.watcher.should_watch_dir(None))


