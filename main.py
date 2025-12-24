from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
import hashlib

app = FastAPI()

SECRET_KEY = "CHANGE_THIS"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# -------- PASSWORD HELPERS --------
def normalize_password(password: str) -> str:
    raw = password.encode("utf-8")
    print("RAW PASSWORD BYTES:", len(raw))   # DEBUG LINE
    return hashlib.sha256(raw).hexdigest()

def hash_password(password: str) -> str:
    return pwd_context.hash(normalize_password(password))


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(normalize_password(password), hashed)

# -------- JWT --------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

# -------- USER DB (HASH ONCE ONLY) --------
fake_users_db = {
    "vinod": {
        "username": "admin",
        "password": hash_password("password123")  # KEEP SHORT
    }
}

# -------- AUTH --------
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload["sub"]

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token}

@app.get("/calculate")
def calculate(a: int, b: int, user=Depends(get_current_user)):
    return {"user": user, "result": a + b}
