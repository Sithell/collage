from abc import ABC, abstractmethod
import typing
from chat import Chat


class ChatsStorage(ABC):
    @abstractmethod
    def get(self, chat_id: int) -> Chat:
        pass

    @abstractmethod
    def set(self, chat_id: int, chat: Chat) -> bool:
        pass

    @abstractmethod
    def __contains__(self, chat_id: int) -> bool:
        pass


class SimpleChatsStorage(ChatsStorage):
    chats: typing.Dict[int, dict] = {}

    def print_all(self):
        print(self.chats[788277446])

    def get(self, chat_id: int) -> Chat:
        if chat_id in self.chats:
            return Chat.from_dict(self.chats[chat_id])  # because we store chats as dict, not Chat objects

        return None

    def set(self, chat_id: int, chat: Chat) -> bool:
        is_new = chat_id not in self.chats
        self.chats[chat_id] = chat.to_dict()
        return is_new

    def __contains__(self, chat_id: int) -> bool:
        return chat_id in self.chats
