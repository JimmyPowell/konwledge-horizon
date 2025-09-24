from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from redis import Redis

from app import models, schemas
from app.api import deps
from app.services import auth_service
from app.utils.response import Success, BadRequest, NotFound, Created, Unauthorized
from app.config.mysql_config import get_mysql_db
from app.config.redis_config import get_redis_client

router = APIRouter()

@router.post("/request-code")
async def request_code(
    request: schemas.EmailRequest,
    db: Session = Depends(get_mysql_db),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Request a verification code for registration.
    """
    success = await auth_service.request_verification_code(db, redis_client, request.email)
    if not success:
        return BadRequest(message="Email already registered")
    return Success(message="Verification code sent")

@router.post("/verify-code")
def verify_code(
    request: schemas.CodeVerify,
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Verify the code and get a session token for registration.
    """
    session_token = auth_service.verify_code_and_create_session(redis_client, request.email, request.code)
    if not session_token:
        return BadRequest(message="Invalid or expired code")
    return Success(data={"session": session_token})

@router.post("/register")
def register_user(
    request: schemas.UserCreate,
    db: Session = Depends(get_mysql_db),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Finalize user registration.
    """
    new_user = auth_service.finalize_registration(db, redis_client, request.session, request.username, request.password)
    if not new_user:
        return BadRequest(message="Invalid session, username taken, or other error")
    
    # Manually create a dict from the user model to avoid ORM issues in response
    user_data = schemas.UserResponse.from_orm(new_user).dict()
    return Created(data=user_data)

@router.post("/login")
def login_for_access_token(
    request: schemas.UserLogin,
    db: Session = Depends(get_mysql_db)
):
    """
    Login to get access and refresh tokens (for regular clients with JSON body).
    """
    user = auth_service.authenticate_user(db, identifier=request.identifier, password=request.password)
    if not user:
        return Unauthorized(message="Incorrect username or password")
    
    tokens = auth_service.generate_tokens(user)
    return Success(data=tokens.dict())

@router.post("/token", response_model=schemas.Token)
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_mysql_db)
):
    """
    Login for Swagger UI authorization (form data).
    """
    user = auth_service.authenticate_user(db, identifier=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = auth_service.generate_tokens(user)
    return tokens

@router.post("/refresh")
def refresh_token(
    request: schemas.TokenRefreshRequest,
    db: Session = Depends(get_mysql_db),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Refresh access token.
    """
    tokens = auth_service.refresh_access_token(db, redis_client, request.refresh_token)
    if not tokens:
        return Unauthorized(message="Invalid or expired refresh token")
    return Success(data=tokens.dict())

@router.post("/logout")
def logout(
    request: schemas.LogoutRequest,
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Logout by blacklisting the refresh token.
    """
    success = auth_service.logout_user(redis_client, request.refresh_token)
    if not success:
        return BadRequest(message="Invalid refresh token")
    return Success(message="Logged out successfully")

@router.post("/change-password")
def change_password(
    request: schemas.ChangePasswordRequest,
    db: Session = Depends(get_mysql_db),
    redis_client: Redis = Depends(get_redis_client),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Change user password.
    """
    error = auth_service.change_user_password(
        db, redis_client, current_user, request.old_password, request.new_password, request.refresh_token
    )
    if error == "invalid_old_password":
        return BadRequest(message="Invalid old password")
    if error == "password_is_the_same":
        return BadRequest(message="New password cannot be the same as the old password")
        
    return Success(message="Password changed successfully")
