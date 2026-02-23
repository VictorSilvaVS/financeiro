from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, LargeBinary
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base
from argon2 import PasswordHasher
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import jwt
import hmac
import hashlib
import sys
import json
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
STATIC_DIR = os.getenv("STATIC_DIR")
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

# Validation
required_configs = ["SECRET_KEY", "ALGORITHM", "DATABASE_URL", "STATIC_DIR", "TEMPLATES_DIR"]
for config in required_configs:
    if os.getenv(config) is None:
        raise RuntimeError(f"Configuração crítica ausente no .env: {config}")
VAULT_KEY_FILE = "vault.key"
VAULT_MASTER_SECRET = os.getenv("VAULT_MASTER_SECRET")

if VAULT_MASTER_SECRET:
    if not os.path.exists(VAULT_KEY_FILE):
        with open(VAULT_KEY_FILE, "w") as f:
            f.write(VAULT_MASTER_SECRET)
        print(f"INFO: Master Secret do .env replicado para '{VAULT_KEY_FILE}' (Backup)")
else:
    if os.path.exists(VAULT_KEY_FILE):
        with open(VAULT_KEY_FILE, "r") as f:
            VAULT_MASTER_SECRET = f.read().strip()
        print(f"INFO: Chave mestra carregada de '{VAULT_KEY_FILE}'")
    else:
        import secrets
        VAULT_MASTER_SECRET = secrets.token_hex(32)
        with open(VAULT_KEY_FILE, "w") as f:
            f.write(VAULT_MASTER_SECRET)
        print(f"INFO: Nova chave mestra gerada e salva em '{VAULT_KEY_FILE}'")
        print("MANTENHA ESTE ARQUIVO SEGURO! Ele é a única forma de recuperar seus dados.")
def derive_vault_key(master_secret: str):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"Vault_Fortress_v3_Salt",
        info=b"Vault_Encryption_Deployment_v1",
    )
    return hkdf.derive(master_secret.encode())

derived_key = derive_vault_key(VAULT_MASTER_SECRET)
aesgcm = AESGCM(derived_key)

ph = PasswordHasher(
    time_cost=4,
    memory_cost=102400,
    parallelism=8
)

limiter = Limiter(key_func=get_remote_address)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def encrypt_val(val: str, user: "User") -> bytes:
    nonce = os.urandom(12)
    aad = f"{user.username}:{user.hashed_password}".encode()
    ct = aesgcm.encrypt(nonce, val.encode(), aad)
    return nonce + ct

def decrypt_val(val: bytes, user: "User") -> str:
    if not val: return ""
    try:
        nonce = val[:12]
        ct = val[12:]
        aad = f"{user.username}:{user.hashed_password}".encode()
        return aesgcm.decrypt(nonce, ct, aad).decode('utf-8')
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="SYSTEM_LOCK: Violação de integridade física detectada no Vault."
        )

def generate_atomic_token(user: "User", **fields) -> str:
    data_str = "|".join(f"{k}:{v}" for k, v in sorted(fields.items()))
    msg = f"{user.id}:{user.username}:{data_str}".encode()
    return hmac.new(derived_key, msg, hashlib.sha256).hexdigest()

def verify_record_integrity(record, user: "User", fields_to_sign: list):
    data = {f: getattr(record, f) for f in fields_to_sign}
    expected = generate_atomic_token(user, **data)
    if not hasattr(record, 'integrity_token') or not record.integrity_token or not hmac.compare_digest(record.integrity_token, expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ATOMIC_FAILURE: Integridade do registro comprometida. Vault Trancado."
        )

# --- MODELS ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    enc_settings = Column(LargeBinary, nullable=True) 
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
    integrity_token = Column(String) # ASSINATURA ATÔMICA
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="transactions")

class Caixinha(Base):
    __tablename__ = "caixinhas"
    id = Column(Integer, primary_key=True, index=True)
    enc_name = Column(LargeBinary)
    enc_target = Column(LargeBinary)
    enc_current = Column(LargeBinary)
    integrity_token = Column(String) # ASSINATURA ATÔMICA
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="caixinhas")

Base.metadata.create_all(bind=engine)

# --- SECURITY LOGIC ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

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

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Sessão expirada. Autentique-se novamente.")

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
app = FastAPI(title="Vault Secure")
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
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "frame-ancestors 'none';"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

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
    access_token = create_access_token(data={"sub": new_user.username})
    response = JSONResponse(content={"message": "Criptografia estabelecida", "access_token": access_token})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="strict",
        secure=False, 
    )
    return response

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
    response = JSONResponse(content={"message": "Bem-vindo ao Vault", "access_token": access_token})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="strict",
        secure=False, 
    )
    return response

@app.post("/logout")
def logout_endpoint():
    response = JSONResponse(content={"message": "Vault Trancado"})
    response.delete_cookie("access_token")
    return response

import json

@app.get("/api/settings")
def get_settings(current_user: User = Depends(get_current_user)):
    if current_user.enc_settings:
        try:
            return json.loads(decrypt_val(current_user.enc_settings, current_user))
        except HTTPException:
            return {
                "theme": "dark",
                "primaryColor": "#6366f1",
                "fontSize": "16px",
                "currency": "BRL",
                "language": "pt-BR"
            }
    return {
        "theme": "dark",
        "primaryColor": "#6366f1",
        "fontSize": "16px",
        "currency": "BRL",
        "language": "pt-BR"
    }

@app.post("/api/settings")
def save_settings(settings: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.enc_settings = encrypt_val(json.dumps(settings), current_user)
    db.commit()
    return {"message": "Configurações aplicadas e criptografadas"}

@app.get("/api/data")
def get_user_data(current_user: User = Depends(get_current_user)):
    transactions = []
    t_fields = ["type", "enc_category", "enc_description", "enc_amount", "enc_total_amount", "installments", "current_installment", "date"]
    for t in current_user.transactions:
        verify_record_integrity(t, current_user, t_fields)
        transactions.append({
            "id": t.id,
            "type": t.type,
            "category": decrypt_val(t.enc_category, current_user) if t.enc_category else None,
            "description": decrypt_val(t.enc_description, current_user),
            "amount": float(decrypt_val(t.enc_amount, current_user)),
            "total_amount": float(decrypt_val(t.enc_total_amount, current_user)),
            "installments": t.installments,
            "current_installment": t.current_installment,
            "date": t.date
        })
            
    caixinhas = []
    c_fields = ["enc_name", "enc_target", "enc_current"]
    for c in current_user.caixinhas:
        verify_record_integrity(c, current_user, c_fields)
        caixinhas.append({
            "id": c.id,
            "name": decrypt_val(c.enc_name, current_user),
            "target": float(decrypt_val(c.enc_target, current_user)),
            "current": float(decrypt_val(c.enc_current, current_user))
        })
            
    return {
        "username": current_user.username,
        "transactions": transactions,
        "caixinhas": caixinhas
    }

@app.post("/api/transactions")
def add_transaction(t: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = {
        "type": t['type'],
        "enc_category": encrypt_val(t.get('category', ''), current_user) if t.get('category') else None,
        "enc_description": encrypt_val(t['description'], current_user),
        "enc_amount": encrypt_val(str(t['amount']), current_user),
        "enc_total_amount": encrypt_val(str(t.get('totalAmount', t['amount'])), current_user),
        "installments": int(t.get('installments', 1)),
        "current_installment": int(t.get('currentInstallment', 1)),
        "date": t.get('date', datetime.now().strftime("%d/%m/%Y"))
    }
    data["integrity_token"] = generate_atomic_token(current_user, **data)
    new_t = Transaction(**data, user_id=current_user.id)
    db.add(new_t)
    db.commit()
    return {"message": "Registro Assinado e Salvo"}

@app.delete("/api/transactions/{t_id}")
def delete_transaction(t_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = db.query(Transaction).filter(Transaction.id == t_id, Transaction.user_id == current_user.id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Não encontrado")
    
    t_fields = ["type", "enc_category", "enc_description", "enc_amount", "enc_total_amount", "installments", "current_installment", "date"]
    verify_record_integrity(t, current_user, t_fields)
    
    db.delete(t)
    db.commit()
    return {"message": "Eliminado"}

@app.post("/api/caixinhas")
def create_caixinha(c: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = {
        "enc_name": encrypt_val(c['name'], current_user),
        "enc_target": encrypt_val(str(c['target']), current_user),
        "enc_current": encrypt_val("0.0", current_user)
    }
    data["integrity_token"] = generate_atomic_token(current_user, **data)
    new_c = Caixinha(**data, user_id=current_user.id)
    db.add(new_c)
    db.commit()
    return {"message": "Reserva Assinada"}

@app.post("/api/caixinhas/{c_id}/deposit")
def deposit(c_id: int, data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Caixinha).filter(Caixinha.id == c_id, Caixinha.user_id == current_user.id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Inexistente")
    
    c_fields = ["enc_name", "enc_target", "enc_current"]
    verify_record_integrity(c, current_user, c_fields)
    
    curr = float(decrypt_val(c.enc_current, current_user))
    amount = float(data['amount'])
    new_total = curr + amount
    
    c.enc_current = encrypt_val(str(new_total), current_user)
    c.integrity_token = generate_atomic_token(current_user, enc_name=c.enc_name, enc_target=c.enc_target, enc_current=c.enc_current)
    
    t_data = {
        "type": "expense",
        "enc_category": encrypt_val("fixed", current_user),
        "enc_description": encrypt_val(f"Reserva: {decrypt_val(c.enc_name, current_user)}", current_user),
        "enc_amount": encrypt_val(str(amount), current_user),
        "enc_total_amount": encrypt_val(str(amount), current_user),
        "date": datetime.now().strftime("%d/%m/%Y")
    }
    t_data["integrity_token"] = generate_atomic_token(current_user, **t_data)
    
    new_t = Transaction(**t_data, user_id=current_user.id)
    db.add(new_t)
    db.commit()
    return {"message": "Depósito Atômico Concluído"}

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
