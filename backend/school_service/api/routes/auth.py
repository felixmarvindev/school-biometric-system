"""API routes for Authentication."""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from school_service.core.database import get_db
from school_service.core.config import settings
from school_service.core.security import create_access_token, decode_access_token
from school_service.services.user_service import UserService
from shared.schemas.user import UserLogin, Token, UserResponse, UserCreate

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


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (Protected)",
    description="""
    Register a new user account. This endpoint requires authentication.
    
    Only authenticated users (typically school admins) can create additional users for their school.
    The user will be associated with a school and will have the 'school_admin' role by default.
    Password must meet strength requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*)
    """,
    responses={
        201: {
            "description": "User registered successfully",
            "model": UserResponse,
        },
        400: {
            "description": "Invalid input data or validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Email 'user@example.com' is already registered"
                    }
                }
            },
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Could not validate credentials"
                    }
                }
            },
        },
        403: {
            "description": "Permission denied - can only create users for your own school",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "You can only create users for your own school"
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
        },
    },
)
async def register(
    user_data: UserCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account (requires authentication).
    
    - **email**: User email address (must be unique)
    - **first_name**: User first name (1-100 characters)
    - **last_name**: User last name (1-100 characters)
    - **password**: User password (must meet strength requirements)
    - **school_id**: ID of the school this user belongs to (must match current user's school)
    - **role**: User role (defaults to 'school_admin')
    
    Returns the created user (without password).
    
    Note: Users can only create accounts for their own school.
    """
    # Security check: Users can only create users for their own school
    if user_data.school_id != current_user.school_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create users for your own school",
        )
    
    user_service = UserService(db)
    
    try:
        user = await user_service.create_user(user_data)
        return UserResponse.model_validate(user)
    except ValueError as e:
        # Handle validation errors (email already exists, weak password, etc.)
        error_msg = str(e)
        
        # Check if it's a bcrypt password length error and provide a user-friendly message
        if "72 bytes" in error_msg.lower() or "truncate" in error_msg.lower():
            error_msg = "Password cannot be longer than 72 bytes. Please use a shorter password."
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )
    except Exception as e:
        # Log the actual error for debugging (in production, use proper logging)
        import traceback
        error_msg = str(e)
        
        # Check if it's a bcrypt password length error
        if "72 bytes" in error_msg.lower() or "truncate" in error_msg.lower():
            error_msg = "Password cannot be longer than 72 bytes. Please use a shorter password."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
        
        error_detail = error_msg if settings.DEBUG else "An error occurred while registering the user"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail,
        )

