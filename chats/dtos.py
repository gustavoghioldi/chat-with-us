from dataclasses import dataclass

@dataclass
class ChatContentDTO:
    datetime: str
    request: str
    response: str
