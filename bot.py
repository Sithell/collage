import random
import typing
from telegram import Update
from telegram.ext import Updater, CallbackContext, MessageHandler, Filters, CommandHandler
from chats_storage import ChatsStorage, SimpleChatsStorage, Chat
import strings


def chat_decorator(func):
    def wrapper(self, update, *args, **kwargs):
        if 'chat' not in kwargs or not isinstance(kwargs['chat'], Chat):
            if update.message.chat_id not in self.chats:
                chat = Chat(update.message.chat_id)
                self.chats.set(chat.id, chat)

            else:
                chat = self.chats.get(update.message.chat_id)

            kwargs['chat'] = chat

        result = func(self, update, *args, **kwargs)
        if isinstance(result, Chat):
            self.chats.set(result.id, result)

        return result

    return wrapper


class Bot:
    state_handlers: typing.Dict[int, typing.Callable]
    chats: ChatsStorage

    def __init__(self, token: str):
        self.chats = SimpleChatsStorage()

        self.state_handlers = {
            Chat.States.START: self.action_start,
            Chat.States.IDLE: self.action_idle,
            Chat.States.WAIT_FOR_ARCHIVE: self.action_got_archive,
            Chat.States.WAIT_FOR_COLLAGE_COUNT: self.action_submit_collage
        }

        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', self.action_start))
        self.dispatcher.add_handler(CommandHandler('collage', self.action_collage))
        self.dispatcher.add_handler(MessageHandler(~Filters.command, self.handle_message))
        self.dispatcher.add_handler(MessageHandler(Filters.command, self.undefined_command))

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    # HANDLERS

    @chat_decorator
    def handle_message(self, update: Update, context: CallbackContext, chat: Chat = None) -> None:
        return self.state_handlers[chat.state](update, context, chat=chat)

    @chat_decorator
    def action_collage(self, update: Update, context: CallbackContext, chat: Chat = None):
        update.message.reply_text(strings.send_archive)
        chat.state = Chat.States.WAIT_FOR_ARCHIVE
        return chat

    @chat_decorator
    def undefined_command(self, update: Update, context: CallbackContext, chat: Chat = None):
        update.message.reply_text(random.choice(strings.what))

    # ACTIONS
    @chat_decorator
    def action_start(self, update: Update, context: CallbackContext, chat: Chat = None) -> Chat:
        user = update.effective_user
        locale = update.effective_user.language_code

        update.message.reply_text(strings.welcome.format(user.username))
        chat.state = Chat.States.IDLE
        return chat

    @chat_decorator
    def action_idle(self, update: Update, context: CallbackContext, chat: Chat = None) -> Chat:
        update.message.reply_text(random.choice(strings.what))

    @chat_decorator
    def action_got_archive(self, update: Update, context: CallbackContext, chat: Chat = None) -> Chat:
        update.message.reply_text(strings.send_collage_count.format(1, 300))
        chat.state = Chat.States.WAIT_FOR_COLLAGE_COUNT
        return chat

    @chat_decorator
    def action_submit_collage(self, update: Update, context: CallbackContext, chat: Chat = None) -> Chat:
        update.message.reply_text(strings.start_making_collage)
        chat.state = Chat.States.IDLE
        return chat
