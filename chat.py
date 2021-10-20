from telegram import File


class Chat:
    id: int
    state: int
    archive: File
    collage_count: int
    min_collage_count: int = 1
    max_collage_count: int = 300

    class States:
        START = 0
        IDLE = 1
        WAIT_FOR_ARCHIVE = 2
        WAIT_FOR_COLLAGE_COUNT = 3

    def __init__(
            self,
            chat_id: int,
            state: int = States.START,
            archive: File = None,
            collage_count: int = None,
            min_collage_count: int = 1,
            max_collage_count: int = 300
    ):
        allowed_states = [v for k, v in Chat.States.__dict__.items() if not k.startswith('__')]
        if state not in allowed_states:
            raise AttributeError("Invalid state")

        self.id = chat_id
        self.state = state
        self.archive = archive
        self.collage_count = collage_count
        self.min_collage_count = min_collage_count
        self.max_collage_count = max_collage_count

    @classmethod
    def from_dict(cls, data: dict):
        return cls(*[data[x] for x in [
            'id', 'state', 'archive', 'collage_count', 'min_collage_count', 'max_collage_count'
        ]])

    def to_dict(self):
        return {
            'id': self.id,
            'state': self.state,
            'archive': self.archive,
            'collage_count': self.collage_count,
            'min_collage_count': self.min_collage_count,
            'max_collage_count': self.max_collage_count,
        }
