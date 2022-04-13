from pydantic import BaseModel


class NumberVariables(BaseModel):
    name: str
    number: int


class NameVariables(BaseModel):
    name: str
