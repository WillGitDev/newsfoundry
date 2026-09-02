from database import init_db, engine
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import bcrypt
import jwt
import os
from sqlmodel import Session, select
from models import LoginRequest, User, Chat, MessageRequest, RevueRequest
from fastapi.middleware.cors import CORSMiddleware
from pydantic_ai import ModelMessagesTypeAdapter
from pydantic_core import to_json
import json
from pydantic_ai.exceptions import ModelAPIError, ModelHTTPError
from datetime import datetime, timezone
from agents import agent, revue_agent

app = FastAPI()
security = HTTPBearer()

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
    """Convertit l'historique brut de PydanticAI (parts typées) en liste simple
    de messages {role, content, timestamp} pour l'affichage frontend.
    Les parts d'appels d'outils (tool-call/tool-return) sont ignorées.
    """
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
        #On refresh pour récupérer l'id.
        session.refresh(chat)
        return {"id": chat.id, "created_at": chat.created_at}

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
        #Transforme le JSON en un objet PydanticAI typés ModelMessage pour l'agent.
        history = ModelMessagesTypeAdapter.validate_python(chat.messages)
        try:
            result = await agent.run(message.content, message_history=history)
        except ModelHTTPError as e:
            if e.status_code == 429:
                raise HTTPException(status_code=429, detail="Crédit épuisé, réessayez plus tard")
            raise HTTPException(status_code=500, detail="Erreur du service d'IA")
        except ModelAPIError:
            raise HTTPException(status_code=504, detail="Le service d'IA n'a pas répondu")
        
        chat.messages = json.loads(to_json(result.all_messages()))
        session.add(chat)
        session.commit()

        return {"response": result.output}

@app.post("/chats/{chat_id}/revue")
async def generate_revue(chat_id: int, revue_request: RevueRequest, user_id: int = Depends(get_current_user_id)):
    with Session(engine) as session:
        chat = session.get(Chat, chat_id)
        if not chat or chat.user_id != user_id:
            raise HTTPException(status_code=404, detail="Chat introuvable")

        history = ModelMessagesTypeAdapter.validate_python(chat.messages)
        revue_date = datetime.now(timezone.utc)
        try:
            result = await revue_agent.run(f"Le sujet choisi par l'utilisateur pour la revue : {revue_request.sujet}" f"La date du jour est : {revue_date.strftime('%d %B %Y')}.", message_history=history)
        except ModelHTTPError as e:
            if e.status_code == 429:
                raise HTTPException(status_code=429, detail="Crédit épuisé, réessayez plus tard")
            raise HTTPException(status_code=500, detail="Erreur du service d'IA")
        except ModelAPIError:
            raise HTTPException(status_code=504, detail="Le service d'IA n'a pas répondu")

        chat.titre = result.output.titre
        chat.synthese_generale = result.output.synthese_generale
        chat.synthese_articles = [synthese_article.model_dump() for synthese_article in result.output.synthese_articles]
        chat.revue_generated_at = revue_date
        session.add(chat)
        session.commit()

        return {
            "titre": chat.titre,
            "synthese_generale": chat.synthese_generale,
            "synthese_articles": chat.synthese_articles,
            "revue_generated_at": chat.revue_generated_at,
        }

@app.get("/revues")
async def list_revues(user_id: int = Depends(get_current_user_id)):
    with Session(engine) as session:
        statement = select(Chat).where(Chat.user_id == user_id, Chat.revue_generated_at != None)
        revues = session.exec(statement).all()

        return [
            {
                "id": revue.id,
                "titre": revue.titre,
                "synthese_generale": revue.synthese_generale,
                "synthese_articles": revue.synthese_articles,
                "revue_generated_at": revue.revue_generated_at,
            }
            for revue in revues
        ]

if __name__ == "__main__":
    init_db()

    uvicorn.run(app, host="0.0.0.0", port=8000)
