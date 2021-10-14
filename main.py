from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from configparser import ConfigParser
from zipfile import ZipFile
from time import time_ns
import requests
import os
from PIL import Image
from random import randint


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def process_file(update: Update, context: CallbackContext) -> None:
    print('Received a file: {}'.format(update.message.document.file_name))

    filename = 'temp/input_' + str(time_ns())[:-10]
    with open(filename, 'wb') as f:
        filepath = update.message.document.get_file()['file_path']
        r = requests.get(filepath)
        f.write(r.content)
        print('Downloaded from {} and saved as {}'.format(filepath, filename))

    with ZipFile(filename, 'r') as zip:
        extract(zip, 'temp/in/')

    if not os.path.exists('temp/out'):
        os.makedirs('temp/out')

    make_collage('temp/in/', 'temp/out/')

    file_paths = os.listdir('temp/out')
    with ZipFile('temp/out.zip', 'w') as zip:
        print("Creating zip archive")
        for file in file_paths:
            print("Add {} to the archive".format(file))
            zip.write('temp/out/' + file)

    filesize = os.path.getsize('temp/out.zip')
    print("Sending document of size {}".format(str(int(filesize / 1024 / 1024 * 100) / 100) + ' Mb'))
    context.bot.send_document(update.effective_chat.id, open('temp/out.zip', 'rb'))

    os.remove(filename)
    os.remove('temp/out.zip')
    [os.remove('temp/in/' + x) for x in os.listdir('temp/in')]

def extract(zip, path):
    ''' Извлечь все изображения из архива в папку '''
    # TODO Извлекать только изображения
    # TODO Возможные проблемы с кириллицей
    # TODO Также извлекать картинки из вложенных папок
    zip.extractall(path)


def make_collage(inpath, outpath):
    images = [Image.open(inpath + f) for f in os.listdir(inpath) if os.path.isfile(os.path.join(inpath, f))]
    print("Loaded {} images".format(len(images)))

    MARGIN = 16
    SIZE = 600
    MAX_COUNT = 10

    selects = []

    for i in range(MAX_COUNT):
        img_size = int((SIZE - MARGIN * 3) / 2)
        retry_count = 10
        while retry_count > 0:
            retry_count -= 1
            select = selection(len(images), 4)
            if select not in selects:
                selects.append(select)
                break
        else:
            break

        pack = [convert_to_square(x, img_size) for x in [images[i] for i in select]]

        collage = Image.new('RGB', (SIZE, SIZE), color='white')
        collage.paste(pack[0], (MARGIN, MARGIN, img_size + MARGIN, img_size + MARGIN))
        collage.paste(pack[1], (MARGIN * 2 + img_size, MARGIN, (img_size + MARGIN) * 2, img_size + MARGIN))
        collage.paste(pack[2], (MARGIN, MARGIN * 2 + img_size, img_size + MARGIN, (img_size + MARGIN) * 2))
        collage.paste(pack[3],
                      (MARGIN * 2 + img_size, MARGIN * 2 + img_size, (img_size + MARGIN) * 2, (img_size + MARGIN) * 2))
        filename = "{}img_{}.png".format(outpath, str.rjust(str(i + 1), len(str(MAX_COUNT)), '0'))
        collage.save(filename)
        print("Saved {}".format(filename))


def selection(array_len: int, size: int) -> list:
    indices = []
    for i in range(size):
        while True:
            index = randint(0, array_len - 1)
            if index not in indices:
                indices.append(index)
                break
    return indices


def convert_to_square(image: Image.Image, size=None) -> Image.Image:
    own_size = min(image.width, image.height)
    center = (image.width / 2, image.height / 2)
    box = (center[0] - own_size / 2, center[1] - own_size / 2,
           center[0] + own_size / 2, center[1] + own_size / 2,)

    if size is None:
        return image.crop(box)

    return image.crop(box).resize((int(size), int(size)))


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini', encoding='utf-8')

    updater = Updater(config.get('TELEGRAM', 'token'))
    dispatcher = updater.dispatcher

    # Commands
    for command, handler in {
        'start': start,
        'help': help_command,
    }.items():
        dispatcher.add_handler(CommandHandler(command, handler))

    # Messages
    for rule, handler in {
        Filters.text & ~Filters.command: echo,
        Filters.document: process_file,
    }.items():
        dispatcher.add_handler(MessageHandler(rule, handler))

    updater.start_polling()
    updater.idle()
