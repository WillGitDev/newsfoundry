from typing import Optional
from sqlmodel import SQLModel, Field, JSON
from datetime import datetime, timezone

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str = Field()

class LoginRequest(SQLModel):
    email: str
    password: str

class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    messages: list = Field(default=[], sa_type=JSON)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageRequest(SQLModel):
    content: str