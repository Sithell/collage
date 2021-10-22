import random

import greenstalk
from json import dumps

from PIL import Image

from worker import Worker
import os
from time import time
import requests
from zipfile import ZipFile
import config.beanstalk


class CollageWorker(Worker):
    def handle(self, workload: dict):
        # Пока что это монолитный метод, но его надо разбить
        print("Got a job")
        try:
            archive_link = workload['archive_link']
            collage_count = workload['collage_count']
            chat_id = workload['chat_id']

        except KeyError as e:
            print("Invalid workload:", e)
            return

        # Создаем пустые папки для временных файлов
        seed = str(time()).split('.')[1][:6]
        path = 'temp/{}_{}'.format(chat_id, seed)
        os.makedirs(path + '/in')
        os.makedirs(path + '/out')

        # Скачиваем архив
        r = requests.get(archive_link)

        # Сохраняем архив в файл (можно пропустить?)
        with open(path + '/in.zip', 'wb') as f:
            f.write(r.content)

        # Распаковываем архив в папку in
        with ZipFile(path + '/in.zip') as zip:
            zip.extractall(path + '/in')

        # Создаем коллажи (из папки in в папку out)
        self.make_collage(path + '/in/', path + '/out/', collage_count)

        # Находим все файлы в папке out
        file_paths = os.listdir(path + '/out')

        # Архивируем содержимое папки out
        with ZipFile(path + '/out.zip', 'w') as zip:
            print("Creating zip archive")
            for file in file_paths:
                print("Add {} to the archive".format(file))
                zip.write(path + '/out/' + file)

        # Определяем размер полученного архива (telegram не может отправить больше 50 Мб)
        filesize = os.path.getsize(path + '/out.zip')
        print("Sending document of size {}".format(str(int(filesize / 1024 / 1024 * 100) / 100) + ' Mb'))

        # Ставим джоб на отправку файла пользователю
        with greenstalk.Client((config.beanstalk.host, config.beanstalk.port)) as client:
            client.use(config.beanstalk.message_sender_queue)
            client.put(dumps({
                'chat_id': chat_id,
                'type': 'file',
                'filepath': path + '/out.zip'
            }))

    #  TODO зарефакторить это все
    def make_collage(self, inpath, outpath, count):
        images = [Image.open(inpath + f) for f in os.listdir(inpath) if os.path.isfile(os.path.join(inpath, f))]
        print("Loaded {} images".format(len(images)))

        MARGIN = 16
        SIZE = 600
        MAX_COUNT = count

        selects = []

        for i in range(MAX_COUNT):
            img_size = int((SIZE - MARGIN * 3) / 2)
            retry_count = 10
            while retry_count > 0:
                retry_count -= 1
                select = self.selection(len(images), 4)
                if select not in selects:
                    selects.append(select)
                    break
            else:
                break

            pack = [self.convert_to_square(x, img_size) for x in [images[i] for i in select]]

            collage = Image.new('RGB', (SIZE, SIZE), color='white')
            collage.paste(pack[0], (MARGIN, MARGIN, img_size + MARGIN, img_size + MARGIN))
            collage.paste(pack[1], (MARGIN * 2 + img_size, MARGIN, (img_size + MARGIN) * 2, img_size + MARGIN))
            collage.paste(pack[2], (MARGIN, MARGIN * 2 + img_size, img_size + MARGIN, (img_size + MARGIN) * 2))
            collage.paste(pack[3],
                          (MARGIN * 2 + img_size, MARGIN * 2 + img_size, (img_size + MARGIN) * 2,
                           (img_size + MARGIN) * 2))
            filename = "{}img_{}.png".format(outpath, str.rjust(str(i + 1), len(str(MAX_COUNT)), '0'))
            collage.save(filename)
            print("Saved {}".format(filename))

    def selection(self, array_len: int, size: int) -> list:
        indices = []
        for i in range(size):
            while True:
                index = random.randint(0, array_len - 1)
                if index not in indices:
                    indices.append(index)
                    break
        return indices

    def convert_to_square(self, image: Image.Image, size=None) -> Image.Image:
        own_size = min(image.width, image.height)
        center = (image.width / 2, image.height / 2)
        box = (center[0] - own_size / 2, center[1] - own_size / 2,
               center[0] + own_size / 2, center[1] + own_size / 2,)

        if size is None:
            return image.crop(box)

        return image.crop(box).resize((int(size), int(size)))


if __name__ == '__main__':
    instance = CollageWorker(config.beanstalk.collage_worker_queue)
    instance.run()
