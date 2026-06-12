from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Vipera Spy")
templates = Jinja2Templates(directory="templates")

# Banco de dados
engine = create_engine("sqlite:///vipera.db")
Base = declarative_base()

class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True)
    link_id = Column(String, index=True)
    ip = Column(String)
    user_agent = Column(String)
    location = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home():
    return "<h1>Vipera Spy - Em desenvolvimento</h1>"

# Mais rotas virão: /create-link, /track/{id}, dashboard
print("Vipera Spy rodando!")
