from watchgod import Change, awatch
import asyncio
import shutil
import os
from uuid import uuid4

from helpers import Config, FileWatcher


class MediaServerProcessor(object):
    def __init__(self):
        self.config = Config()
        for directory in self.config['DIRECTORIES']:
            if not os.path.isdir(self.config['DIRECTORIES'][directory]):
                os.makedirs(self.config['DIRECTORIES'][directory])

    async def watch(self):
        async for changes in awatch(self.config['DIRECTORIES']['QUEUE_DIR'], watcher_cls=FileWatcher):
            for type_, path in changes:
                if type_ == Change.added:
                    extension = path.split('.')[-1]
                    file_name = os.path.basename(path)
                    file_name_ = f'{str(uuid4())}.{extension}'

                    if extension in ('jpg', 'jpeg', 'png'):
                        shutil.copy2(path, self.config['DIRECTORIES']['ORIGINALS_DIR'])
                        shutil.move(path, self.config['DIRECTORIES']['TMP_DIR'])
                        os.rename(f'{self.config["DIRECTORIES"]["TMP_DIR"]}/{file_name}',
                                  f'{self.config["DIRECTORIES"]["TMP_DIR"]}/{file_name_}')

                    elif self.config['HARD_DELETE_UNKNOWN_TYPES']:
                        os.remove(path)
                    else:
                        pass


if __name__ == '__main__':
    try:
        app = MediaServerProcessor()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(app.watch())
    except KeyboardInterrupt:
        print('\nStopped watching... Goodbye.')
