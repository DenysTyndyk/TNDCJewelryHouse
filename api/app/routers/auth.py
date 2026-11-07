from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies import get_current_user, get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse, MessageResponse, ForgotPasswordRequest, ResetPasswordRequest
from app.services import auth_service
from app.services.auth_service import AuthError
from app.core.limiter import limiter


router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "refresh_token"

def _set_refresh_cookie(response: Response, refresh_token: str)-> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/auth"
    )

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)):
    auth_service.register(db, payload.email, payload.password, payload.first_name, payload.last_name, payload.phone_number)
    return MessageResponse(message="If this email is not already registered, a verification link has been sent")

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try: 
        access_token, refresh_token, _ = auth_service.login(db, payload.email, payload.password)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)

@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
def refresh(request: Request, response: Response, refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME), db: Session = Depends(get_db)):
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")
    try:
        access_token, new_refresh_token = auth_service.refresh(db, refresh_token)
    except AuthError as e:
        response.delete_cookie(REFRESH_COOKIE_NAME, path="/auth")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    _set_refresh_cookie(response, new_refresh_token)
    return TokenResponse(access_token=access_token)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
def logout(request: Request, response: Response, refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME), db: Session = Depends(get_db)):
    if refresh_token is not None: 
        auth_service.logout(db, refresh_token)
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/auth")

@router.get("/me", response_model=UserResponse)
def me(user = Depends(get_current_user)):
    return user

@router.get("/verify-email", response_model=MessageResponse)
@limiter.limit("10/minute")
def verify_email(request: Request, token: str, db: Session = Depends(get_db)):
    try:
        auth_service.verify_email(db, token)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return MessageResponse(message="Email verified successfully") 

@router.post("/forgot-password", response_model=MessageResponse)
@limiter.limit("3/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service.forgot_password(db,payload.email)
    return MessageResponse(message="If this email is registered, a reset link has been sent")

@router.post("/reset-password", response_model=MessageResponse)
@limiter.limit("5/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        auth_service.reset_password(db, payload.token, payload.new_password)
    except AuthError as e: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return MessageResponse(message="Password has been reset")