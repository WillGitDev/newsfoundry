from database import init_db, engine
from fastapi import FastAPI, HTTPException
import uvicorn
import bcrypt
import jwt
import os
from sqlmodel import Session, select
from models import LoginRequest, User
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
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

if __name__ == "__main__":
    init_db()

    uvicorn.run(app, host="0.0.0.0", port=8000)
