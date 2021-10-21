from telegram import Bot
from threading import Thread
from worker.worker import Worker


class MessageSender(Worker, Thread):
    def __init__(self, bot: Bot, tube: str):
        # No idea how multiple inheritance works here
        super(Worker, self).__init__()
        super(MessageSender, self).__init__(tube)
        self.bot = bot

    def handle(self, workload: dict):
        try:
            chat_id = workload['chat_id']
            message_type = workload['type']
            if message_type == 'text':
                self.bot.send_message(chat_id, workload['message'])

            elif message_type == 'file':
                with open(workload['filepath'], 'rb') as f:
                    self.bot.send_document(chat_id, f)
            else:
                raise KeyError("Unknown message type: {}".format(message_type))

        except KeyError as e:
            print("Invalid workload:", e)

