from PIL import Image
import random
import os
from zipfile import ZipFile
from time import time
import requests


class ImageService:
    def generate_collage(self, archive_link: str, collage_count: int, callback):
        self.process_file(archive_link, collage_count, callback)

    def process_file(self, archive_link: str, collage_count: int, callback):
        print('Received a file: {}'.format(archive_link))

        filename = 'temp/input_' + str(time())
        with open(filename, 'wb') as f:
            r = requests.get(archive_link)
            f.write(r.content)
            print('Downloaded from {} and saved as {}'.format(archive_link, filename))

        with ZipFile(filename, 'r') as zip:
            self.extract(zip, 'temp/in/')

        if not os.path.exists('temp/out'):
            os.makedirs('temp/out')

        self.make_collage('temp/in/', 'temp/out/', collage_count)

        file_paths = os.listdir('temp/out')
        with ZipFile('temp/out.zip', 'w') as zip:
            print("Creating zip archive")
            for file in file_paths:
                print("Add {} to the archive".format(file))
                zip.write('temp/out/' + file)

        filesize = os.path.getsize('temp/out.zip')
        print("Sending document of size {}".format(str(int(filesize / 1024 / 1024 * 100) / 100) + ' Mb'))
        callback(open('temp/out.zip', 'rb'))

        os.remove(filename)
        os.remove('temp/out.zip')
        [os.remove('temp/in/' + x) for x in os.listdir('temp/in')]
        [os.remove('temp/out/' + x) for x in os.listdir('temp/out')]

    def extract(self, zip, path):
        ''' Извлечь все изображения из архива в папку '''
        # TODO Извлекать только изображения
        # TODO Возможные проблемы с кириллицей
        # TODO Также извлекать картинки из вложенных папок
        zip.extractall(path)

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


