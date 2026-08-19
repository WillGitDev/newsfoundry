from database import init_db, engine
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import bcrypt
import jwt
import os
from sqlmodel import Session, select
from models import LoginRequest, User, Chat, MessageRequest
from fastapi.middleware.cors import CORSMiddleware
from pydantic_ai import Agent, ModelMessagesTypeAdapter
from pydantic_core import to_json
import json

app = FastAPI()
security = HTTPBearer()
agent = Agent(
    "anthropic:claude-haiku-4-5-20251001",
    instructions="Tu es un assistant de journaliste ou de pigistes pour un public français. Tu dois aider les pigistes à gagner du temps et aussi à améliorer la qualité de leurs articles. Sois factuel et professionnel, il faut un contenu journalistique. Demande à l'utilisateur quel style et quelle forme adopter pour ses articles. Pour les revues de presse il faut s'appuyer sur des faits, c'est un point important si tu ne peux pas répondre à la question il faut le dire que tu ne sais pas"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://newsfoundry.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")
    return payload["user_id"]

def simplify_messages(chat_messages):
    simplified = []
    for message in chat_messages:
        for part in message["parts"]:
            if part["part_kind"] == "user-prompt":
                simplified.append({"role": "user", "content": part["content"], "timestamp": part["timestamp"]})
            elif part["part_kind"] == "text":
                simplified.append({"role": "assistant", "content": part["content"], "timestamp": message["timestamp"]})
    return simplified
@app.get("/")
async def hello():
    return {"message": "👋"}

@app.post("/login")
async def login(credentials: LoginRequest):
    with Session(engine) as session:
        statement = select(User).where(User.email == credentials.email)
        user = session.exec(statement).first()

        if not user or not bcrypt.checkpw(credentials.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

        token = jwt.encode({"user_id": user.id}, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

        return {"token": token}

@app.post("/chats")
async def create_chat(user_id: int = Depends(get_current_user_id)):
    with Session(engine) as session:
        chat = Chat(user_id=user_id, messages=[])
        session.add(chat)
        session.commit()
        session.refresh(chat)
        return {"id": chat.id}

@app.get("/chats/{chat_id}")
async def get_chat(chat_id: int, user_id: int = Depends(get_current_user_id)):
    with Session(engine) as session:
        chat = session.get(Chat, chat_id)
        if not chat or chat.user_id != user_id:
            raise HTTPException(status_code=404, detail="Chat introuvable")
        return {"id": chat.id, "messages": simplify_messages(chat.messages)}

@app.get("/chats")
async def list_chats(user_id: int = Depends(get_current_user_id)):
    with Session(engine) as session:
        statement = select(Chat).where(Chat.user_id == user_id)
        chats = session.exec(statement).all()
        return [{"id": chat.id, "created_at": chat.created_at} for chat in chats]

@app.post("/chats/{chat_id}/messages")
async def add_message(chat_id: int, message: MessageRequest, user_id: int = Depends(get_current_user_id)):
    with Session(engine) as session:
        chat = session.get(Chat, chat_id)
        if not chat or chat.user_id != user_id:
            raise HTTPException(status_code=404, detail="Chat introuvable")

        history = ModelMessagesTypeAdapter.validate_python(chat.messages)
        result = await agent.run(message.content, message_history=history)

        chat.messages = json.loads(to_json(result.all_messages()))
        session.add(chat)
        session.commit()

        return {"response": result.output}


if __name__ == "__main__":
    init_db()

    uvicorn.run(app, host="0.0.0.0", port=8000)
