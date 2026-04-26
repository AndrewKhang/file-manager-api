from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import UserRegister, UserResponse, Token
from app.auth import hash_password, verify_password, create_access_token
from app.auth import get_current_user, require_admin
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
import secrets
from fastapi.responses import RedirectResponse
from app.email import send_verification_email
import os

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister, db: Session = Depends(get_db)):
    # Check existed email 
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check existed username 
    existing = db.query(models.User).filter(models.User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = models.User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password)
    )
    token = secrets.token_urlsafe(32)
    user.verification_token = token
    user.token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    db.add(user)
    db.flush()                                    # assign id without committing
    await send_verification_email(user.email, token)  # send first; if fails, DB auto-rollbacks
    db.commit()                                   # only commit after email sent successfully
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)  # response_model filters out sensitive fields like hashed_password
def me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.get("/admin/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):  # require_admin blocks non-admin roles
    return db.query(models.User).all()

@router.delete("/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(require_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_files = db.query(models.File).filter(models.File.owner_id == user_id).all()
    for f in user_files:
     if os.path.exists(f.file_path):
        os.remove(f.file_path)
     db.delete(f)
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted"}


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    if user.token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")
    user.is_verified = True
    user.verification_token = None
    user.token_expires_at = None
    db.commit()
    return RedirectResponse(url="/login.html")