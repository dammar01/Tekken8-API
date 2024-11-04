from pydantic import BaseModel


class Notation(BaseModel):
    character_name: str | None = None
    notation: str


class Movetable(BaseModel):
    character_name: str
    notation: str | None = None
