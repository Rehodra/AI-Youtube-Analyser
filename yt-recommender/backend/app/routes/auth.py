from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import RedirectResponse
from datetime import datetime
from typing import Optional

from app.schemas.schemas import UserRegister, UserLogin, TokenResponse, UserResponse, ProfileUpdate, PlanUpdate
from app.utils.auth import hash_password, verify_password, create_jwt, get_current_user
from app.services import mongo_client
from app.services.cloudinary_service import upload_avatar, delete_avatar
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user with email, username, and password
    """
    # Check if email already exists
    existing_user = await mongo_client.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await mongo_client.get_user_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user document
    user_doc = {
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "password_hash": hash_password(user_data.password),
        "avatar_url": None,
        "avatar_public_id": None,
        "oauth_provider": None,
        "oauth_id": None,
        "total_jobs": 0,
        "active_jobs": 0,
        "plan": "free",
        "credits_used": 0,
        "credits_limit": 100,
        "job_ids": [],
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Insert user
    user_id = await mongo_client.create_user(user_doc)
    
    # Create JWT token
    token = create_jwt(user_id, user_data.email)
    
    # Return response
    user_response = UserResponse(
        user_id=user_id,
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        avatar_url=None,
        plan="free",
        credits_used=0,
        credits_limit=100,
        is_verified=False
    )
    
    return TokenResponse(token=token, user=user_response)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login with email and password
    """
    # Get user by email
    user = await mongo_client.get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user has password (not OAuth user)
    if not user.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please login with Google OAuth"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create JWT token
    token = create_jwt(user["_id"], user["email"])
    
    # Return response
    user_response = UserResponse(
        user_id=user["_id"],
        email=user["email"],
        username=user["username"],
        full_name=user.get("full_name"),
        avatar_url=user.get("avatar_url"),
        plan=user.get("plan", "free"),
        credits_used=user.get("credits_used", 0),
        credits_limit=user.get("credits_limit", 100),
        is_verified=user.get("is_verified", False)
    )
    
    return TokenResponse(token=token, user=user_response)


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user profile
    """
    
    return UserResponse(
        user_id=str(user["_id"]),
        email=user["email"],
        username=user.get("username", ""),
        full_name=user.get("full_name"),
        avatar_url=user.get("avatar_url"),
        plan=user.get("plan", "free"),
        credits_used=user.get("credits_used", 0),
        credits_limit=user.get("credits_limit", 100),
        is_verified=user.get("is_verified", False)
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    user: dict = Depends(get_current_user)
):
    """
    Update user profile (name, username)
    """
    user_id = user["_id"]
    update_data = {"updated_at": datetime.utcnow()}
    
    if profile_data.full_name is not None:
        update_data["full_name"] = profile_data.full_name
    
    if profile_data.username is not None:
        # Check if username is already taken by another user
        existing = await mongo_client.get_user_by_username(profile_data.username)
        if existing and existing["_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        update_data["username"] = profile_data.username
    
    # Update user
    success = await mongo_client.update_user(user_id, update_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    # Get updated user
    user = await mongo_client.get_user_by_id(user_id)
    
    return UserResponse(
        user_id=user["_id"],
        email=user["email"],
        username=user["username"],
        full_name=user.get("full_name"),
        avatar_url=user.get("avatar_url"),
        plan=user.get("plan", "free"),
        credits_used=user.get("credits_used", 0),
        credits_limit=user.get("credits_limit", 100),
        is_verified=user.get("is_verified", False)
    )


@router.post("/upload-avatar", response_model=UserResponse)
async def upload_user_avatar(
    avatar: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Upload or update user profile picture to Cloudinary
    """
    user_id = user["_id"]
    # Validate file type
    if not avatar.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Read file content
    file_content = await avatar.read()
    
    # Get current user to check for existing avatar
    user = await mongo_client.get_user_by_id(user_id)
    
    # Delete old avatar if exists
    if user.get("avatar_public_id"):
        try:
            await delete_avatar(user["avatar_public_id"])
        except Exception:
            pass  # Continue even if deletion fails
    
    # Upload to Cloudinary
    try:
        result = await upload_avatar(file_content, user_id)
        
        # Update user document
        update_data = {
            "avatar_url": result["url"],
            "avatar_public_id": result["public_id"],
            "updated_at": datetime.utcnow()
        }
        
        await mongo_client.update_user(user_id, update_data)
        
        # Get updated user
        user = await mongo_client.get_user_by_id(user_id)
        
        return UserResponse(
            user_id=user["_id"],
            email=user["email"],
            username=user["username"],
            full_name=user.get("full_name"),
            avatar_url=user.get("avatar_url"),
            plan=user.get("plan", "free"),
            credits_used=user.get("credits_used", 0),
            credits_limit=user.get("credits_limit", 100),
            is_verified=user.get("is_verified", False)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload avatar: {str(e)}"
        )


@router.delete("/avatar", response_model=UserResponse)
async def delete_user_avatar(user: dict = Depends(get_current_user)):
    """
    Remove user profile picture
    """
    user_id = user["_id"]
    
    if user.get("avatar_public_id"):
        try:
            await delete_avatar(user["avatar_public_id"])
        except Exception:
            pass  # Continue even if deletion fails
    
    # Update user document
    update_data = {
        "avatar_url": None,
        "avatar_public_id": None,
        "updated_at": datetime.utcnow()
    }
    
    await mongo_client.update_user(user_id, update_data)
    
    # Get updated user
    user = await mongo_client.get_user_by_id(user_id)
    
    return UserResponse(
        user_id=user["_id"],
        email=user["email"],
        username=user["username"],
        full_name=user.get("full_name"),
        avatar_url=user.get("avatar_url"),
        plan=user.get("plan", "free"),
        credits_used=user.get("credits_used", 0),
        credits_limit=user.get("credits_limit", 100),
        is_verified=user.get("is_verified", False)
    )


@router.put("/plan", response_model=UserResponse)
async def update_plan(
    plan_data: PlanUpdate,
    user: dict = Depends(get_current_user)
):
    """
    Update user's pricing plan
    """
    user_id = user["_id"]
    
    # Validate plan
    valid_plans = ["free", "pro", "team"]
    plan = plan_data.plan.lower()
    
    if plan not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Must be one of: {', '.join(valid_plans)}"
        )
    
    # Update credits limit based on plan
    credits_limit = 100  # free
    if plan == "pro":
        credits_limit = 1000
    elif plan == "team":
        credits_limit = 10000
    
    # Update user
    update_data = {
        "plan": plan,
        "credits_limit": credits_limit,
        "updated_at": datetime.utcnow()
    }
    
    success = await mongo_client.update_user(user_id, update_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update plan"
        )
    
    # Get updated user
    user = await mongo_client.get_user_by_id(user_id)
    
    return UserResponse(
        user_id=user["_id"],
        email=user["email"],
        username=user["username"],
        full_name=user.get("full_name"),
        avatar_url=user.get("avatar_url"),
        plan=user.get("plan", "free"),
        credits_used=user.get("credits_used", 0),
        credits_limit=user.get("credits_limit", 100),
        is_verified=user.get("is_verified", False)
    )


@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(user: dict = Depends(get_current_user)):
    """
    Delete user account permanently
    """
    user_id = user["_id"]
    
    # Delete avatar from Cloudinary if exists
    if user.get("avatar_public_id"):
        try:
            await delete_avatar(user["avatar_public_id"])
        except Exception:
            pass
    
    # Delete user from database
    success = await mongo_client.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
    
    return None
