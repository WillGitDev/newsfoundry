from fastapi.testclient import TestClient
from main import app
from database import engine
from models import User
from sqlmodel import Session, select
import bcrypt
import os
import jwt

client = TestClient(app)

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