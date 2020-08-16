import re
import os

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
        self['SOURCE_SET'] = [(100, 100), (250, 250)]
        self['COMPRESSION'] = 0

        # What to do with unknown file types (not png, jpg or jpeg)
        self['HARD_DELETE_UNKNOWN_TYPES'] = True

        #
        self[''] = False

        def load():
            # TODO: Load a yaml file into the config class
            pass


class FileWatcher(DefaultDirWatcher):
    """
    Used to watch the directory for changes.
    """

    def __init__(self, root_path):
        self.include_pattern = re.compile(r"^[._]")
        super().__init__(root_path)

    def should_watch_file(self, entry):
        """
        Returns whether or not the file should be watched. Ignores all files starting with a '.' or '_'

        Parameters
        ----------
        entry : os.DirEntry
            The file that was found in the directory.

        Returns
        -------
        bool
            Whether or not the file should be watched.
        """
        return not self.include_pattern.match(entry.name)

    def should_watch_dir(self, entry):
        """
        Returns false, so directory changes are ignored.

        Parameter
        ---------
        entry : os.DirEntry
            The directory that was changed in the main directory.

        Returns
        -------
        False : bool
            Directories should be ignored, thus the value False is always returned.
        """
        return False


def add_id_to_img(path):
    i = 1
    while os.path.exists(path):
        path = f'{path}-{i}'
        i = i + 1

    return path
