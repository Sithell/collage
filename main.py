from configparser import ConfigParser
from bot import Bot

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini', encoding='utf-8')

    bot = Bot(config.get('TELEGRAM', 'token'))
    bot.run()
