class Chat:
    id: int
    state: int

    class States:
        START = 0
        IDLE = 1
        WAIT_FOR_ARCHIVE = 2
        WAIT_FOR_COLLAGE_COUNT = 3

    def __init__(self, chat_id: int, state: int = States.START):
        allowed_states = [v for k, v in Chat.States.__dict__.items() if not k.startswith('__')]
        if state not in allowed_states:
            raise AttributeError("Invalid state")

        self.id = chat_id
        self.state = state

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data['id'], data['state'])

    def to_dict(self):
        return {
            'id': self.id,
            'state': self.state,
        }
