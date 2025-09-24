import random
import string
import json
from typing import Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from redis import Redis
from app import crud, models, schemas
from app.utils import security
from . import mail_service

# --- Registration Logic ---

async def request_verification_code(db: Session, redis_client: Redis, email: str) -> bool:
    """
    Handles the logic for requesting a verification code.
    Returns True if code was sent, False if user already exists.
    """
    if crud.crud_user.get_user_by_email(db, email=email):
        return False  # User already exists

    code = ''.join(random.choices(string.digits, k=6))
    
    # Send email using the mail service
    await mail_service.send_verification_code(email_to=email, code=code)

    # Store code and verification status in Redis
    redis_key = f"verification:{email}"
    redis_data = {"code": code, "verified": False}
    redis_client.set(redis_key, json.dumps(redis_data), ex=300)  # 5-minute expiry

    return True

def verify_code_and_create_session(redis_client: Redis, email: str, code: str) -> Optional[str]:
    """
    Verifies the code. If correct, updates Redis and returns a new session token.
    """
    redis_key = f"verification:{email}"
    stored_data = redis_client.get(redis_key)

    if not stored_data:
        return None # Code expired or email not found

    data = json.loads(stored_data)
    if data["code"] != code:
        return None # Invalid code

    # Update status to verified
    data["verified"] = True
    redis_client.set(redis_key, json.dumps(data), ex=300)

    # Create a session token
    session_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    session_key = f"session:{session_token}"
    redis_client.set(session_key, email, ex=300) # Link session to email

    return session_token

def finalize_registration(db: Session, redis_client: Redis, session: str, username: str, password: str) -> Optional[models.User]:
    """
    Finalizes user registration after session validation.
    """
    session_key = f"session:{session}"
    email = redis_client.get(session_key)

    if not email:
        return None # Invalid or expired session

    email = email.decode('utf-8')
    
    # Double-check verification status
    verification_key = f"verification:{email}"
    verification_data = redis_client.get(verification_key)
    if not verification_data or not json.loads(verification_data).get("verified"):
        return None # Email not verified

    if crud.crud_user.get_user_by_username(db, username=username):
        return None # Username already taken

    user_data = {"email": email, "username": username, "password": password}
    new_user = crud.crud_user.create_user(db, user_data=user_data)

    # Clean up Redis keys
    redis_client.delete(session_key)
    redis_client.delete(verification_key)

    return new_user

# --- Login Logic ---

def authenticate_user(db: Session, identifier: str, password: str) -> Optional[models.User]:
    """
    Authenticates a user by username or email.
    """
    user = crud.crud_user.get_user_by_username(db, username=identifier)
    if not user:
        user = crud.crud_user.get_user_by_email(db, email=identifier)
    
    if not user:
        return None # User not found
        
    if not security.verify_password(password, user.hashed_password):
        return None # Invalid password
        
    return user

def generate_tokens(user: models.User) -> schemas.Token:
    """
    Generates access and refresh tokens for a user.
    """
    access_token = security.create_access_token(
        data={"sub": user.uuid, "role": user.role}
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user.uuid}
    )
    return schemas.Token(access_token=access_token, refresh_token=refresh_token)

# --- Token Management ---

def refresh_access_token(db: Session, redis_client: Redis, refresh_token: str) -> Optional[schemas.Token]:
    """
    Refreshes an access token using a valid refresh token.
    """
    if security.is_token_blacklisted(redis_client, refresh_token):
        return None # Token is blacklisted

    payload = security.decode_token(refresh_token)
    if not payload:
        return None # Invalid token

    user_uuid = payload.get("sub")
    user = crud.crud_user.get_user_by_uuid(db, uuid=user_uuid)
    if not user:
        return None # User not found

    # Generate new access token
    new_access_token = security.create_access_token(data={"sub": user.uuid, "role": user.role})
    
    # Check refresh token expiry
    exp_timestamp = payload.get("exp")
    if exp_timestamp:
        expire_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        if expire_time - datetime.now(timezone.utc) < timedelta(hours=24):
            # Issue a new refresh token and blacklist the old one
            new_refresh_token = security.create_refresh_token(data={"sub": user.uuid})
            
            # Blacklist the old refresh token until it expires
            expires_in = int((expire_time - datetime.now(timezone.utc)).total_seconds())
            security.add_token_to_blacklist(redis_client, refresh_token, expires_in)
            
            return schemas.Token(access_token=new_access_token, refresh_token=new_refresh_token)

    return schemas.Token(access_token=new_access_token, refresh_token=None)


def logout_user(redis_client: Redis, refresh_token: str) -> bool:
    """
    Logs out a user by blacklisting their refresh token.
    """
    payload = security.decode_token(refresh_token)
    if not payload:
        return False # Invalid token

    exp_timestamp = payload.get("exp")
    if not exp_timestamp:
        return False # No expiration in token

    expire_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    expires_in = int((expire_time - datetime.now(timezone.utc)).total_seconds())
    
    if expires_in > 0:
        security.add_token_to_blacklist(redis_client, refresh_token, expires_in)
    
    return True

def change_user_password(db: Session, redis_client: Redis, user: models.User, old_password: str, new_password: str, refresh_token: str) -> Optional[str]:
    """
    Changes a user's password and blacklists the old refresh token.
    Returns an error string on failure, None on success.
    """
    if not security.verify_password(old_password, user.hashed_password):
        return "invalid_old_password"

    if old_password == new_password:
        return "password_is_the_same"

    # Update password
    crud.crud_user.update_user_password(db, user_id=user.id, new_password=new_password)

    # Blacklist the associated refresh token
    payload = security.decode_token(refresh_token)
    if payload:
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            expire_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            expires_in = int((expire_time - datetime.now(timezone.utc)).total_seconds())
            if expires_in > 0:
                security.add_token_to_blacklist(redis_client, refresh_token, expires_in)

    return None
