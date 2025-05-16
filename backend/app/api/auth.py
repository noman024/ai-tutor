from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.services.user_service import get_user_by_email, create_user, authenticate_user
from backend.app.core.security import create_access_token, decode_access_token
from pydantic import BaseModel, EmailStr
import logging
from fastapi.security import OAuth2PasswordBearer
from backend.app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt: {data.email}")
    if get_user_by_email(db, data.email):
        logger.warning(f"Registration failed: Email already registered: {data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        user = create_user(db, data.email, data.password)
        logger.info(f"Registration successful: {data.email}")
        return {"id": user.id, "email": user.email}
    except Exception as e:
        logger.error(f"Registration error for {data.email}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt: {data.email}")
    user = authenticate_user(db, data.email, data.password)
    if not user:
        logger.warning(f"Login failed: Invalid credentials for {data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.email})
    logger.info(f"Login successful: {data.email}")
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception
    email = payload["sub"]
    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user 