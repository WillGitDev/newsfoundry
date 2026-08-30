from database import init_db, engine
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import bcrypt
import jwt
import os
from sqlmodel import Session, select
from models import LoginRequest, User, Chat, MessageRequest, RevuesOutput, RevueRequest
from fastapi.middleware.cors import CORSMiddleware
from pydantic_ai import Agent, ModelMessagesTypeAdapter
from pydantic_core import to_json
import json
from anthropic import RateLimitError, APIError, APIConnectionError
from world_news import get_daily_prompt, get_search_news
from datetime import datetime, timezone



app = FastAPI()
security = HTTPBearer()
agent = Agent(
    "anthropic:claude-haiku-4-5-20251001",
    instructions="Tu es un assistant de journaliste ou de pigistes pour un public français. Tu dois aider les pigistes à gagner du temps et aussi à améliorer la qualité de leurs articles. Sois factuel et professionnel, il faut un contenu journalistique. Demande à l'utilisateur quel style et quelle forme adopter pour ses articles. Pour les revues de presse il faut s'appuyer sur des faits, c'est un point important si tu ne peux pas répondre à la question il faut le dire que tu ne sais pas"
)

revue_agent = Agent(
    "anthropic:claude-haiku-4-5-20251001",
    instructions="Tu es un assistant de journaliste ou de pigistes pour un public français. Tu dois faire une revue en t'appuyant sur toute la discussion " \
    "de tous les articles et une synthèse pour chaque article. Pour la synthèse générale, commence par une ligne \"REVUE DE PRESSE [SUJET] - jour Mois annnée\" ," \
    "Pour le jour mois année met le jour en chiffre, le mois en lettre avec la première lettre en majuscule et l'année en chiffre (exemple: 30 Septembre 2025)" \
    "Utilise la date exacte qui te sera donnée dans le message, ne l'invente jamais. Pour la mise en forme du reste du contenue mes listes à puces et des saut de ligne entre chaque liste à puces",
    output_type=RevuesOutput,
)

@agent.system_prompt
async def add_daily_news() -> str:
    content = await get_daily_prompt()
    return f"Voici les actualités du jour, à utiliser comme source d'information à jour :\n{content}"

@agent.tool_plain
async def search_news(query: str) -> str:
    """Recherche des articles d'actualité sur un sujet précis. 
    À utiliser quand l'utilisateur veut plus d'informations sur un thème donné."""
    search = await get_search_news(query)
    return f"Voici les résultats de la recherche :\n{search}"

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

        history = ModelMessagesTypeAdapter.validate_python(chat.messages)
        try:
            result = await agent.run(message.content, message_history=history)
        except RateLimitError:
            raise HTTPException(status_code=429, detail="Crédit épuisé, réessayez plus tard")
        except APIConnectionError as e:
            if "504" in str(e) or "timeout" in str(e).lower():
                raise HTTPException(status_code=504, detail="Traitement indisponible")
            else:
                raise HTTPException(status_code=529, detail="Service temporairement indisponible")
        except APIError as e:
            raise HTTPException(status_code=500, detail="Erreur serveur")
        
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
        except RateLimitError:
            raise HTTPException(status_code=429, detail="Crédit épuisé, réessayer plus tard")
        except APIConnectionError as e:
            if "504" in str(e) or "timeout" in str(e).lower():
                raise HTTPException(status_code=504, detail="Traitement indisponible")
            else:
                raise HTTPException(status_code=529, detail="Service temporairement indisponible")
        except APIError as e:
            raise HTTPException(status_code=500, detail="Erreur serveur")

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
