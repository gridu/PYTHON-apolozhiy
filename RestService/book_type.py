from enum import Enum
from datetime import datetime
from json import JSONEncoder


class BookType(Enum):
    SCIENCE_FICTION = "Science Fiction"
    SATIRE = "Satire"
    DRAMA = "Drama"
    ACTION_AND_ADVENTURE = "Action and Adventure"
    ROMANCE = "Romance"

    def __str__(self):
        return str(self.value)


class BookEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, BookType):
            return o.value
        elif isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        else:
            super().default(self, o)
