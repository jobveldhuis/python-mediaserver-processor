import re

from watchgod import DefaultDirWatcher, Change


class Config(dict):
    """
    Configuration class, behaves like a standard dict.
    """

    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)

        # Standard configuration settings, please do not overwrite but load using yaml template
        # Directories
        self['DIRECTORIES'] = {
            'QUEUE_DIR': './queue',
            'OUT_DIR': './out',
            'TMP_DIR': './tmp',
            'ORIGINALS_DIR': './originals'
        }

        # Actions
        self['SOURCE_SET'] = []
        self['COMPRESSION'] = 0

        # Maximum amount of concurrent errors (max. 99)
        self['CONCURRENT_ERROR_LIMIT'] = 5

        # What to do with unknown file types (not png, jpg or jpeg)
        self['HARD_DELETE_UNKNOWN_TYPES'] = True

        def load():
            # TODO: Load a yaml file into the config class
            pass


class FileWatcher(DefaultDirWatcher):
    def __init__(self, root_path):
        self.ignore_pattern = re.compile(r"^\.")
        super().__init__(root_path)

    def should_watch_file(self, entry):
        return not self.ignore_pattern.match(entry.name)

    def should_watch_dir(self, entry):
        return False
