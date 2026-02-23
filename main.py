from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
from typing import Optional
import uvicorn
import os

# --- LOAD CONFIGURATION FROM .ENV ---
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
DATABASE_URL = os.getenv("DATABASE_URL")
VAULT_KEY_PATH = os.getenv("VAULT_KEY_PATH")
STATIC_DIR = os.getenv("STATIC_DIR")
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

# Validation to ensure no hardcodes are effectively used via defaults
required_configs = [
    "SECRET_KEY", "ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES", 
    "DATABASE_URL", "VAULT_KEY_PATH", "STATIC_DIR", 
    "TEMPLATES_DIR", "HOST", "PORT"
]

for config in required_configs:
    if os.getenv(config) is None:
        raise RuntimeError(f"Configuração crítica ausente no .env: {config}")

# --- ABSURD SECURITY CONFIGURATION ---
if not os.path.exists(VAULT_KEY_PATH):
    master_key = Fernet.generate_key()
    with open(VAULT_KEY_PATH, "wb") as f:
        f.write(master_key)
else:
    with open(VAULT_KEY_PATH, "rb") as f:
        master_key = f.read()

cipher_suite = Fernet(master_key)
ph = PasswordHasher() # Argon2id
limiter = Limiter(key_func=get_remote_address)

# --- DATABASE SETUP ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- UTILS FOR ABSURD ENCRYPTION ---
def encrypt_val(val: str) -> bytes:
    return cipher_suite.encrypt(val.encode())

def decrypt_val(val: bytes) -> str:
    return cipher_suite.decrypt(val).decode()

# --- MODELS ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    enc_settings = Column(LargeBinary, nullable=True) # NEW: Encrypted JSON settings
    transactions = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")
    caixinhas = relationship("Caixinha", back_populates="owner", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    enc_category = Column(LargeBinary, nullable=True)
    enc_description = Column(LargeBinary)
    enc_amount = Column(LargeBinary)
    enc_total_amount = Column(LargeBinary)
    installments = Column(Integer, default=1)
    current_installment = Column(Integer, default=1)
    date = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="transactions")

class Caixinha(Base):
    __tablename__ = "caixinhas"
    id = Column(Integer, primary_key=True, index=True)
    enc_name = Column(LargeBinary)
    enc_target = Column(LargeBinary)
    enc_current = Column(LargeBinary)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="caixinhas")

Base.metadata.create_all(bind=engine)

# --- SECURITY LOGIC ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise HTTPException(status_code=401)
    except:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None: raise HTTPException(status_code=401)
    return user

# --- APP SETUP ---
app = FastAPI(title="🛡️ Antigravity Secure Vault")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# --- ROUTES ---
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/signup")
@limiter.limit("5/minute")
def signup(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Usuário já protegido no sistema")
    hashed_pwd = ph.hash(form_data.password)
    new_user = User(username=form_data.username, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"message": "Criptografia estabelecida"}

@app.post("/token")
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Credenciais Inválidas")
    try:
        ph.verify(user.hashed_password, form_data.password)
    except:
        raise HTTPException(status_code=400, detail="Credenciais Inválidas")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

import json

@app.get("/api/settings")
def get_settings(current_user: User = Depends(get_current_user)):
    if current_user.enc_settings:
        return json.loads(decrypt_val(current_user.enc_settings))
    return {
        "theme": "dark",
        "primaryColor": "#6366f1",
        "fontSize": "16px",
        "currency": "BRL",
        "language": "pt-BR"
    }

@app.post("/api/settings")
def save_settings(settings: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.enc_settings = encrypt_val(json.dumps(settings))
    db.commit()
    return {"message": "Configurações aplicadas e criptografadas"}

@app.get("/api/data")
def get_user_data(current_user: User = Depends(get_current_user)):
    transactions = []
    for t in current_user.transactions:
        transactions.append({
            "id": t.id,
            "type": t.type,
            "category": decrypt_val(t.enc_category) if t.enc_category else None,
            "description": decrypt_val(t.enc_description),
            "amount": float(decrypt_val(t.enc_amount)),
            "total_amount": float(decrypt_val(t.enc_total_amount)),
            "installments": t.installments,
            "current_installment": t.current_installment,
            "date": t.date
        })
    caixinhas = []
    for c in current_user.caixinhas:
        caixinhas.append({
            "id": c.id,
            "name": decrypt_val(c.enc_name),
            "target": float(decrypt_val(c.enc_target)),
            "current": float(decrypt_val(c.enc_current))
        })
    return {
        "username": current_user.username,
        "transactions": transactions,
        "caixinhas": caixinhas
    }

@app.post("/api/transactions")
def add_transaction(t: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_t = Transaction(
        type=t['type'],
        enc_category=encrypt_val(t.get('category', '')) if t.get('category') else None,
        enc_description=encrypt_val(t['description']),
        enc_amount=encrypt_val(str(t['amount'])),
        enc_total_amount=encrypt_val(str(t.get('totalAmount', t['amount']))),
        installments=int(t.get('installments', 1)),
        current_installment=int(t.get('currentInstallment', 1)),
        date=t['date'],
        user_id=current_user.id
    )
    db.add(new_t)
    db.commit()
    return {"message": "Encriptado e salvo"}

@app.delete("/api/transactions/{t_id}")
def delete_transaction(t_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.id == t_id, Transaction.user_id == current_user.id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Não encontrado na zona segura")
    db.delete(t)
    db.commit()
    return {"message": "Eliminado"}

@app.post("/api/caixinhas")
def create_caixinha(c: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_c = Caixinha(
        enc_name=encrypt_val(c['name']),
        enc_target=encrypt_val(str(c['target'])),
        enc_current=encrypt_val("0.0"),
        user_id=current_user.id
    )
    db.add(new_c)
    db.commit()
    return {"message": "Reserva estabelecida"}

@app.post("/api/caixinhas/{c_id}/deposit")
def deposit(c_id: int, data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Caixinha).filter(Caixinha.id == c_id, Caixinha.user_id == current_user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Inexistente")
    curr = float(decrypt_val(c.enc_current))
    amount = float(data['amount'])
    new_total = curr + amount
    c.enc_current = encrypt_val(str(new_total))
    new_t = Transaction(
        type="expense",
        enc_category=encrypt_val("fixed"),
        enc_description=encrypt_val(f"Reserva: {decrypt_val(c.enc_name)}"),
        enc_amount=encrypt_val(str(amount)),
        enc_total_amount=encrypt_val(str(amount)),
        date=datetime.now().strftime("%d/%m/%Y"),
        user_id=current_user.id
    )
    db.add(new_t)
    db.commit()
    return {"message": "Depósito encriptado com sucesso"}

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
