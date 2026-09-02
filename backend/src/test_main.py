from fastapi.testclient import TestClient
from main import app, agent
from database import engine
from models import User, Chat
from sqlmodel import Session, select
from database import init_db, engine
from pydantic_ai import models
from pydantic_ai.models.test import TestModel
import bcrypt
import os
import jwt

init_db()
client = TestClient(app)
models.ALLOW_MODEL_REQUESTS = False

def test_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "👋"}

def test_user_cannot_access_another_users_chat():
    with Session(engine) as session:
        other_user = User( email="test@second.com",
                        hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8"),
                         )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)
        try:
            other_user_token = jwt.encode({"user_id": other_user.id}, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

            requete = select(User).where(User.email == "test@test.com")
            main_user = session.exec(requete).first()
            main_user_token = jwt.encode({"user_id": main_user.id}, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

            response = client.post("/chats", headers={"Authorization": f"Bearer {main_user_token}"})
            chat_id = response.json()["id"]

            # le deuxième utilisateur essaie d'accéder à un chat qui n'est pas le sien.
            response = client.get(f"/chats/{chat_id}", headers={"Authorization": f"Bearer {other_user_token}"})
            assert response.status_code == 404

            response = client.get(f"/chats/{chat_id}", headers={"Authorization": f"Bearer {main_user_token}"})
            assert response.status_code == 200
        finally:
            session.delete(other_user)
            session.commit()

def test_send_message_creates_chat_history():
    with Session(engine) as session:
        requete = select(User).where(User.email == "test@test.com")
        main_user = session.exec(requete).first()
        token = jwt.encode({"user_id": main_user.id}, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

    response = client.post("/chats", headers={"Authorization": f"Bearer {token}"})
    chat_id = response.json()["id"]

    try:
        # TestModel remplace le vrai LLM : pas d'appel réel à Anthropic pendant le test.
        with agent.override(model=TestModel()):
            response = client.post(
                f"/chats/{chat_id}/messages",
                json={"content": "Bonjour"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        assert "response" in response.json()

        response = client.get(f"/chats/{chat_id}", headers={"Authorization": f"Bearer {token}"})
        messages = response.json()["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Bonjour"
        assert messages[1]["role"] == "assistant"
    finally:
        with Session(engine) as session:
            chat = session.get(Chat, chat_id)
            session.delete(chat)
            session.commit()

def test_user_cannot_modify_another_users_chat():
    with Session(engine) as session:
        other_user = User(
            email="test@third.com",
            hashed_password=bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8"),
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        chat_id = None
        try:
            other_user_token = jwt.encode({"user_id": other_user.id}, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

            requete = select(User).where(User.email == "test@test.com")
            main_user = session.exec(requete).first()
            main_user_token = jwt.encode({"user_id": main_user.id}, os.getenv("JWT_SECRET_KEY"), algorithm="HS256")

            response = client.post("/chats", headers={"Authorization": f"Bearer {main_user_token}"})
            chat_id = response.json()["id"]

            response = client.post(
                f"/chats/{chat_id}/messages",
                json={"content": "Bonjour"},
                headers={"Authorization": f"Bearer {other_user_token}"},
            )
            assert response.status_code == 404

            response = client.post(
                f"/chats/{chat_id}/revue",
                json={"sujet": "politique"},
                headers={"Authorization": f"Bearer {other_user_token}"},
            )
            assert response.status_code == 404
        finally:
            if chat_id:
                session.delete(session.get(Chat, chat_id))
            session.delete(other_user)
            session.commit()