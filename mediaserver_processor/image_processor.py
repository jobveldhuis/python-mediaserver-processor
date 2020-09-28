import asyncio
import shutil
import os

import logging

from watchgod import Change, awatch
from uuid import uuid4
from PIL import Image

from mediaserver_processor.helpers import Config, FileWatcher


class MediaServerProcessor(object):
    """
    The application class that holds most of the logic of the image processor.
    """

    def __init__(self):
        self.config = Config()
        self._validate_directories()
        self.logger = self.configure_logging()

        if self.config['DISABLE_LOGGING']:
            self.logger.disabled = True

        Image.MAX_IMAGE_PIXELS = self.config['MAX_IMAGE_PIXELS']

        if __name__ == '__main__':
            self.broadcast_welcome_message()

        self.logger.info('Succesfully initialized MediaServerProcessor')

        if os.listdir(self.config['DIRECTORIES']['QUEUE_DIR']):
            self.logger.warning('There are still some items in the queue directory. These cannot be processed.')

    async def process_image(self, file):
        """
        Processes a certain image that exists in the TMP_DIR.

        Parameters
        ----------
        file : tuple
            The name and extension of the file to parse.

        Returns
        -------
        None
        """
        name, extension = file
        working_path = f'{self.config["DIRECTORIES"]["TMP_DIR"]}/{name}.{extension}'

        # If the image could not be validated or an error occurs, remove and skip this image
        if not await self._validate_image(working_path):
            if self.config['HARD_DELETE_UNPROCESSABLE']:
                os.remove(f'{self.config["DIRECTORIES"]["ORIGINALS_DIR"]}/{name}.{extension}')
                os.remove(working_path)
                self.logger.warning(f'Image "{name}.{extension}" could not be verified and was removed from queue.')
                return

        # Resize and save image in two formats: original format and webp
        for size in self.config['SOURCE_SET']:
            image = await self.resize_image(working_path, size)

            if self.config['HARD_KEEP_FILE_TYPE']:
                await self.save_image(image, name, extension, size=size[0])

                for type_ in self.config['ALWAYS_SAVE_AS']:
                    if type_ is not extension:
                        await self.save_image(image, name, type_, size=size[0])
            else:
                if await self._has_transparency(image):
                    await self.save_image(image, name, self.config['FILE_TYPE_TRANSPARENT'], size=size[0])

                else:
                    image.mode = 'RGB'
                    await self.save_image(image, name, self.config['FILE_TYPE_NONTRANSPARENT'], size=size[0])

                for type_ in self.config['ALWAYS_SAVE_AS']:
                    if type_ is not self.config['FILE_TYPE_NONTRANSPARENT'] \
                            and type_ is not self.config['FILE_TYPE_TRANSPARENT']:
                        await self.save_image(image, name, type_, size=size[0])

            self.logger.info(f'Saved "{name}.{extension}", size: {size}')

        os.remove(working_path)
        return

    @staticmethod
    async def resize_image(image_path, size):
        """
        Resizes the image with its current ratio intact. Will never upscale an image.

        Parameters
        ----------
        image_path : str
            The path pointing to the temp folder with the image to work with.
        size : tuple
            A tuple containing the desired size, in the form (width, height).
        """
        image = Image.open(image_path)
        image.thumbnail(size)

        return image

    async def save_image(self, image, name, image_format, **kwargs):
        """
        Saves the image to the output folder.

        Parameters
        ----------
        image : PIL.Image
            Image class that holds the image we are working with.
        name : str
            Name the image should be saved to.
        image_format : str
            The format we should save the image in.
        **kwargs
            Optional parameters that set the behaviour of image saving. Allowed: size, optimize.

        Returns
        -------
        None
        """
        width = None
        optimize = None

        for key, value in kwargs.items():
            if key == 'size':
                width = value
            if key == 'optimize':
                optimize = value

        if not width:
            width = image.width

        if not optimize:
            optimize = self.config['OPTIMIZE']

        image.save(f'{self.config["DIRECTORIES"]["OUT_DIR"]}/{name}_{width}.{image_format}', optimize=optimize)

    async def run(self):
        """
        Asynchronous function that watches for new images to be added to the queue.
        When an image is found, it calls self.process_image to actually process the image file.

        Returns
        -------
        None
        """
        async for changes in awatch(self.config['DIRECTORIES']['QUEUE_DIR'], watcher_cls=FileWatcher):
            for type_, path in changes:
                if type_ == Change.added:
                    self.logger.info('Saw a file being added to the queue directory.')
                    extension = path.split('.')[-1]
                    file_name = os.path.basename(path)

                    if self.config['HASH_FILE_NAMES']:
                        new_file_name = str(uuid4())
                    else:
                        new_file_name = os.path.basename(path).split('.')[0]

                    new_path = f'{self.config["DIRECTORIES"]["QUEUE_DIR"]}/{new_file_name}.{extension}'
                    file = (new_file_name, extension)

                    if extension in self.config['ALLOWED_FILE_TYPES']:
                        os.rename(f'{self.config["DIRECTORIES"]["QUEUE_DIR"]}/{file_name}', new_path)
                        shutil.copy2(new_path, self.config['DIRECTORIES']['ORIGINALS_DIR'])
                        shutil.move(new_path, self.config['DIRECTORIES']['TMP_DIR'])

                        await self.process_image(file)

                    elif self.config['HARD_DELETE_UNKNOWN_TYPES']:
                        os.remove(path)
                    else:
                        pass

    def load_config(self, file):
        """
        Load the config from a yaml-file.

        Parameters
        ----------
        file : str
            Relative path to the yaml-file to load.

        Returns
        -------
        None
        """
        self.config.load(file)
        self._validate_directories()

    def _validate_directories(self):
        for directory in self.config['DIRECTORIES']:
            if not os.path.isdir(self.config['DIRECTORIES'][directory]):
                os.makedirs(self.config['DIRECTORIES'][directory])

    async def _validate_image(self, file):
        """
        Basic validation to check if an image is actually an image.

        Parameters
        ----------
        file : str
            Path to the image file to load into the validation.

        Returns
        -------
        bool
            Whether or not the image is an image.
        """
        # noinspection PyBroadException
        try:
            image = Image.open(file)
            image.verify()
        except Exception:
            self.logger.exception(f'Exception occurred when verifying image "{file}"')
            return False
        return True

    @staticmethod
    async def _has_transparency(image):
        """
        Checks whether or not the image contains transparent pixels.

        Parameters
        ----------
        image : PIL.Image
            Loaded image file

        Returns
        -------
        bool
            Whether or not the image contains any transparency.
        """
        if image.mode == 'P':
            transparent = image.info.get('transparency', -1)
            for _, index in image.getcolors():
                if index == transparent:
                    return True
        elif image.mode == 'RGBA':
            extrema = image.getextrema()
            if extrema[3][0] < 255:
                return True
        return False

    def broadcast_welcome_message(self):
        """
        Broadcasts a simple message to the terminal when starting main. All looks, no use.

        Returns
        -------
        None
        """
        print('::::::::::::::::::::::::::::::::')
        print('::   Mediaserver  Processor   ::')
        print('::   Now watching queue dir   ::')

        if self.config['DISABLE_LOGGING']:
            print('::  ------------------------  ::')
            print('::  All logging was disabled  ::')

        print('::::::::::::::::::::::::::::::::')

    def configure_logging(self):
        """
        Configures logging and returns a logger object.

        Returns
        -------
        logger
            The logger that is being used for logging in the project.
        """
        logger = logging.getLogger('media_server_processor')
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(f'{self.config["DIRECTORIES"]["LOG_DIR"]}/mediaserver.log')
        file_handler.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.CRITICAL)

        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S")
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger


if __name__ == '__main__':
    try:
        app = MediaServerProcessor()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(app.run())
    except KeyboardInterrupt:
        print('\nStopped watching... Goodbye.')
