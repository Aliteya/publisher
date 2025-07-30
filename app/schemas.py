from pydantic import BaseModel

class UserInput(BaseModel):
    name: str
    reason: str