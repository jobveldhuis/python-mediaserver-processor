import unittest
from pathlib import Path

import mediaserver_processor
from mediaserver_processor.helpers import is_yaml, load_yaml


class TestConfigurationMethods(unittest.TestCase):
    def setUp(self):
        self.app = mediaserver_processor.MediaServerProcessor()
        self.directory = Path(__file__).parent.absolute()
        self.app.load_config(f'{self.directory}/static/test.yaml')

    def test_is_yaml(self):
        self.assertFalse(is_yaml(f'{self.directory}/static/not_yaml.txt'))
        self.assertTrue(is_yaml(f'{self.directory}/static/test.yaml'))

    def test_boolean(self):
        self.assertTrue(self.app.config['test_bool_true'])
        self.assertFalse(self.app.config['test_bool_false'])

    def test_string(self):
        self.assertEqual(self.app.config['test_string'], 'Hello')
        self.assertEqual(self.app.config['test_string_quotes'], 'World')

    def test_tuple(self):
        self.assertIsInstance(self.app.config['test_tuple'], tuple)
        self.assertNotIsInstance(self.app.config['test_invalid_tuple'], tuple)
        self.assertTupleEqual(self.app.config['test_tuple'], (120, 120))
        self.assertEqual(self.app.config['test_invalid_tuple'], '(120, 120)')

    def test_list(self):
        check = [
            'Monty',
            'Python',
            'and the',
            'Holy',
            'Grail'
        ]
        self.assertIsInstance(self.app.config['test_list'], list)
        self.assertNotIsInstance(self.app.config['test_invalid_list'], list)
        self.assertListEqual(self.app.config['test_list'], check)

    def test_nonexistent_key(self):
        with self.assertRaises(KeyError):
            value = self.app.config['key_that_does_not_exist']
