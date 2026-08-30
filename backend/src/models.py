from typing import Optional
from sqlmodel import SQLModel, Field, JSON
from datetime import datetime, timezone, date as Date
from pydantic import BaseModel

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
    titre: str = Field(default="")
    synthese_generale: str = Field(default="")
    synthese_articles: list = Field(default=[], sa_type=JSON)
    revue_generated_at: Optional[datetime] = Field(default=None)

class MessageRequest(SQLModel):
    content: str

class News(SQLModel, table=True):
    date: Date = Field(primary_key=True)
    content: str = Field()

class ArticleSynthese(BaseModel):
    titre: str
    synthese: str

class RevuesOutput(BaseModel):
    titre: str
    synthese_generale: str
    synthese_articles: list[ArticleSynthese]

class RevueRequest(SQLModel):
    sujet: str