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
        self['ALLOWED_FILE_TYPES'] = ['jpg', 'jpeg', 'png']
        self['DEFAULT_FILE_TYPE_TRANSPARENT'] = 'png'
        self['DEFAULT_FILE_TYPE_NONTRANSPARENT'] = 'jpeg'
        self['ALWAYS_SAVE_AS'] = ['webp']
        self['SOURCE_SET'] = [(100, 100), (250, 250)]
        self['COMPRESSION'] = 0

        # What to do with unknown file types (not png, jpg or jpeg) or unprocessable images
        self['HARD_DELETE_UNKNOWN_TYPES'] = True
        self['HARD_DELETE_UNPROCESSABLE'] = True

        # Safety feature to check for malicious files to be uploaded (Decompression Bombs)
        self['MAX_IMAGE_PIXELS'] = 10000000
        self['IGNORE_COMPRESSION_BOMBS'] = True

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
