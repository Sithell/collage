from bot import Bot
import config.telegram

if __name__ == '__main__':
    bot = Bot(config.telegram.token)
    bot.run()
