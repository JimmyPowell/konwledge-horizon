from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import hash_password
import uuid

def get_user_by_uuid(db: Session, uuid: str) -> User:
    return db.query(User).filter(User.uuid == uuid).first()

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user_data: dict) -> User:
    hashed_password = hash_password(user_data["password"])
    db_user = User(
        uuid=str(uuid.uuid4()),
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user_id: int, new_password: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.hashed_password = hash_password(new_password)
        db.commit()
        db.refresh(user)
    return user
