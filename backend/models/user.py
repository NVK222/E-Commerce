from sqlmodel import Field,SQLModel
from pydantic import BaseModel

class User(SQLModel, table = True):
    id: int | None = Field(default = None, primary_key = True)
    username: str = Field(max_length = 32)
    email: str = Field(max_length = 64)
    password: str = Field(max_length = 256)
    isadmin : bool = Field(default = False)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: str