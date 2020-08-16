from watchgod import Change, awatch
import asyncio
import shutil
import os
from uuid import uuid4
from PIL import Image

from mediaserver_processor.helpers import Config, FileWatcher, add_id_to_img


class MediaServerProcessor(object):
    """
    The application class that holds most of the logic of the image processor.
    """
    def __init__(self):
        self.config = Config()
        for directory in self.config['DIRECTORIES']:
            if not os.path.isdir(self.config["DIRECTORIES"][directory]):
                os.makedirs(self.config["DIRECTORIES"][directory])

    async def process_image(self, file):
        name, extension = file
        working_path = f'{self.config["DIRECTORIES"]["TMP_DIR"]}/{name}.{extension}'

        for size in self.config['SOURCE_SET']:
            image = Image.open(working_path)
            image.thumbnail(size)
            width, height = size

            image.save(f'{self.config["DIRECTORIES"]["OUT_DIR"]}/{name}_'
                       f'{width}x{height}.{extension}')

        os.remove(working_path)
        return

    async def run(self):
        """
        Asynchronous function that watches for new images to be added to the queue

        :return:
        """
        async for changes in awatch(self.config['DIRECTORIES']['QUEUE_DIR'], watcher_cls=FileWatcher):
            for type_, path in changes:
                if type_ == Change.added:
                    extension = path.split('.')[-1]
                    file_name = os.path.basename(path)
                    file_name_ = str(uuid4())
                    new_path = f'{self.config["DIRECTORIES"]["QUEUE_DIR"]}/{file_name_}.{extension}'
                    file = (file_name_, extension)

                    if extension in ('jpg', 'jpeg', 'png'):
                        os.rename(f'{self.config["DIRECTORIES"]["QUEUE_DIR"]}/{file_name}', new_path)
                        shutil.copy2(new_path, self.config['DIRECTORIES']['ORIGINALS_DIR'])
                        shutil.move(new_path, self.config['DIRECTORIES']['TMP_DIR'])

                        await self.process_image(file)

                    elif self.config['HARD_DELETE_UNKNOWN_TYPES']:
                        os.remove(path)
                    else:
                        pass


if __name__ == '__main__':
    try:
        app = MediaServerProcessor()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(app.run())
    except KeyboardInterrupt:
        print('\nStopped watching... Goodbye.')
