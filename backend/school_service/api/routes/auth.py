"""API routes for Authentication."""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.core.database import get_db
from school_service.core.config import settings
from school_service.core.security import create_access_token, decode_access_token
from school_service.services.user_service import UserService
from shared.schemas.user import UserLogin, Token, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="""
    Authenticate a user and return a JWT access token.
    
    The token should be included in subsequent requests in the Authorization header:
    `Authorization: Bearer <token>`
    """,
    responses={
        200: {
            "description": "Login successful",
            "model": Token,
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect email or password"
                    }
                }
            },
        },
    },
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    User login endpoint.
    
    - **username**: User email address (OAuth2PasswordRequestForm uses 'username' field)
    - **password**: User password
    
    Returns a JWT access token on successful authentication.
    """
    user_service = UserService(db)
    
    # Authenticate user (OAuth2PasswordRequestForm uses 'username' for email)
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # 'sub' is standard JWT claim for subject
            "email": user.email,
            "school_id": user.school_id,
            "role": user.role,
        }
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/login/json",
    response_model=Token,
    summary="User login (JSON body)",
    description="""
    Alternative login endpoint that accepts JSON body instead of form data.
    
    This is more convenient for frontend applications using JSON.
    """,
    responses={
        200: {
            "description": "Login successful",
            "model": Token,
        },
        401: {
            "description": "Invalid credentials",
        },
    },
)
async def login_json(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    User login endpoint (JSON body version).
    
    - **email**: User email address
    - **password**: User password
    
    Returns a JWT access token on successful authentication.
    """
    user_service = UserService(db)
    
    # Authenticate user
    user = await user_service.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "school_id": user.school_id,
            "role": user.role,
        }
    )
    
    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Dependency to get current authenticated user from JWT token.
    
    This can be used in route dependencies to require authentication.
    
    Example:
        @router.get("/protected")
        async def protected_route(current_user: UserResponse = Depends(get_current_user)):
            return {"user": current_user}
    """
    from school_service.services.user_service import UserService
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    # Get user ID from token
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_user_by_id(int(user_id))
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return UserResponse.model_validate(user)

