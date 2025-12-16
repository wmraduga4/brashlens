"""API endpoints для работы с пользователями."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from app.services.user_service import UserService
from app.api.dependencies import get_user_service
from app.schemas.user import UserResponse, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    telegram_id: int = Query(..., description="Telegram user ID"),
    service: UserService = Depends(get_user_service)
):
    """
    Получить данные текущего пользователя по Telegram ID
    
    Используется ботом и Mini App для получения информации о пользователе
    """
    user = await service.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found"
        )
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """
    Создать нового пользователя
    
    Используется ботом при первом взаимодействии пользователя
    """
    try:
        user = await service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """Получить пользователя по ID"""
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service)
):
    """Обновить данные пользователя"""
    user = await service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


@router.get("", response_model=List[UserResponse])
async def get_users(
    role: str = Query(None, description="Filter by role"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: UserService = Depends(get_user_service)
):
    """Получить список пользователей с фильтрацией"""
    if role:
        users = await service.get_users_by_role(role, skip, limit)
    else:
        # TODO: добавить метод get_all в следующей итерации
        users = []
    return users
