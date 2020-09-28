import re
import os

import yaml
from watchgod import DefaultDirWatcher
import logging


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
            'ORIGINALS_DIR': './originals',
            'LOG_DIR': './logs'
        }

        # Actions
        self['ALLOWED_FILE_TYPES'] = ['jpg', 'jpeg', 'png']
        self['FILE_TYPE_TRANSPARENT'] = 'png'
        self['FILE_TYPE_NONTRANSPARENT'] = 'jpeg'
        self['ALWAYS_SAVE_AS'] = ['webp']
        self['SOURCE_SET'] = [(100, 100), (250, 250)]
        self['OPTIMIZE'] = True
        self['HASH_FILE_NAMES'] = False
        self['PROCESS_LEFTOVER_IMAGES'] = True

        # What to do with unknown file types (not png, jpg or jpeg) or unprocessable images
        self['HARD_KEEP_FILE_TYPE'] = True
        self['HARD_DELETE_UNKNOWN_TYPES'] = True
        self['HARD_DELETE_UNPROCESSABLE'] = True

        # Safety feature to check for malicious files to be uploaded (Decompression Bombs)
        self['MAX_IMAGE_PIXELS'] = 10000000
        self['IGNORE_COMPRESSION_BOMBS'] = True

        # Settings for logging
        self['DISABLE_LOGGING'] = False
        self['LOG_LEVEL'] = logging.INFO
        self['LOG_FILE_NAME'] = 'mediaserver'

    def load(self, file):
        """
        Add key/value pairs to the configuration. Overwrite where necessary.

        Parameters
        ----------
        file : str
            Relative path to the yaml-file to load into the configuration.

        Returns
        -------
        None
        """
        dictionary = load_yaml(file)
        for item in dictionary:
            self[item] = dictionary[item]


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


def is_yaml(path):
    """
    Checks whether the file at path is a yaml-file.

    Parameters
    ----------
    path : str
        The relative path to the file that should be checked.

    Returns
    -------
    bool
        Whether or not the specified file is a yaml-file.
    """
    if path.endswith('.yaml') or path.endswith('.yml'):
        return True
    return False


def load_yaml(file):
    """
    Loads a yaml-file into a Python dictionary.

    Parameters
    ----------
    file : str
        Relative path to the file that should be loaded into a dict.

    Raises
    ------
    ValueError
        When specified file is not a yaml-file, and thus, cannot be loaded.

    Returns
    -------
    items : dict
        The dictionary that was retrieved from the Yaml-file.
    """
    if not is_yaml(file):
        raise ValueError()

    with open(file, 'r') as f:
        items = yaml.load(f, Loader=yaml.FullLoader)

    return items
