from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app import crud, models
from app.config.mysql_config import get_mysql_db
from app.utils import security

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_mysql_db)
) -> models.User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_uuid = payload.get("sub")
    if user_uuid is None:
        raise credentials_exception
        
    user = crud.crud_user.get_user_by_uuid(db, uuid=user_uuid)
    if user is None:
        raise credentials_exception
        
    return user
