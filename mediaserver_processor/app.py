from watchgod import Change, awatch
import asyncio
import shutil
import os
from uuid import uuid4
from PIL import Image

from mediaserver_processor.helpers import Config, FileWatcher


# TODO: Add logging for MediaServerProcessor, so people know what is happening
class MediaServerProcessor(object):
    """
    The application class that holds most of the logic of the image processor.
    """

    def __init__(self):
        self.config = Config()
        for directory in self.config['DIRECTORIES']:
            if not os.path.isdir(self.config['DIRECTORIES'][directory]):
                os.makedirs(self.config['DIRECTORIES'][directory])

        Image.MAX_IMAGE_PIXELS = self.config['MAX_IMAGE_PIXELS']
        self._broadcast_welcome_message()

    async def process_image(self, file):
        name, extension = file
        working_path = f'{self.config["DIRECTORIES"]["TMP_DIR"]}/{name}.{extension}'

        # If the image could not be validated or an error occurs, remove and skip this image
        if not await self._validate_image(working_path):
            if self.config['HARD_DELETE_UNPROCESSABLE']:
                os.remove(f'{self.config["DIRECTORIES"]["ORIGINALS"]}/{name}.{extension}')
                os.remove(working_path)
                return

        # Resize and save image in two formats: original format and webp
        for size in self.config['SOURCE_SET']:
            image = await self.resize_image(working_path, size)

            if await self._has_transparency(image):
                await self.save_image(image, name, self.config['DEFAULT_FILE_TYPE_TRANSPARENT'])

            else:
                image.mode = 'RGB'
                await self.save_image(image, name, self.config['DEFAULT_FILE_TYPE_NONTRANSPARENT'])

            for type_ in self.config['ALWAYS_SAVE_AS']:
                if type_ is not self.config['DEFAULT_FILE_TYPE_NONTRANSPARENT'] \
                        and type_ is not self.config['DEFAULT_FILE_TYPE_TRANSPARENT']:
                    await self.save_image(image, name, type_)

        os.remove(working_path)
        return

    @staticmethod
    async def resize_image(image_path, size):
        image = Image.open(image_path)
        width, height = size

        if not height:
            image.thumbnail(width)
        else:
            image.thumbnail(size)

        return image

    async def save_image(self, image, name, image_format):
        image.save(f'{self.config["DIRECTORIES"]["OUT_DIR"]}/{name}_{image.width}.{image_format}')

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
                    extension = path.split('.')[-1]
                    file_name = os.path.basename(path)
                    file_name_ = str(uuid4())
                    new_path = f'{self.config["DIRECTORIES"]["QUEUE_DIR"]}/{file_name_}.{extension}'
                    file = (file_name_, extension)

                    if extension in self.config['ALLOWED_FILE_TYPES']:
                        os.rename(f'{self.config["DIRECTORIES"]["QUEUE_DIR"]}/{file_name}', new_path)
                        shutil.copy2(new_path, self.config['DIRECTORIES']['ORIGINALS_DIR'])
                        shutil.move(new_path, self.config['DIRECTORIES']['TMP_DIR'])

                        await self.process_image(file)

                    elif self.config['HARD_DELETE_UNKNOWN_TYPES']:
                        os.remove(path)
                    else:
                        pass

    @staticmethod
    async def _validate_image(file):
        # noinspection PyBroadException
        try:
            image = Image.open(file)
            image.verify()
        except Exception:
            return False
        return True

    @staticmethod
    async def _has_transparency(image):
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

    @staticmethod
    def _broadcast_welcome_message():
        print('WELCOME')


if __name__ == '__main__':
    try:
        app = MediaServerProcessor()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(app.run())
    except KeyboardInterrupt:
        print('\nStopped watching... Goodbye.')
