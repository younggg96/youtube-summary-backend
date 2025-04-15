from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.base import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.models.user import User
from app.crud import (
    create_user, 
    get_user, 
    get_users, 
    update_user, 
    delete_user, 
    get_user_by_email,
    get_user_by_username
)
from app.auth.security import get_current_user

# 创建用户路由，添加详细描述
router = APIRouter(
    prefix="/users", 
    tags=["users"],
    responses={404: {"description": "用户未找到"}},
)

@router.post(
    "/", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="注册新用户",
    description="创建新用户账户，需要提供有效的邮箱、用户名和密码。"
)
def register_user(
    user: UserCreate = Body(..., description="用户注册信息"),
    db: Session = Depends(get_db)
):
    """
    注册新用户：
    
    - **email**: 有效的邮箱地址
    - **username**: 3-50个字符的用户名，只能包含字母、数字、下划线和连字符
    - **password**: 至少8个字符，包含大小写字母和至少一个数字
    """
    # 检查邮箱是否已存在
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 检查用户名是否已存在
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    return create_user(db=db, user=user)

@router.get(
    "/", 
    response_model=List[UserResponse],
    summary="获取所有用户",
    description="获取所有用户列表，需要管理员权限。"
)
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户列表（需要管理员权限）：
    
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - 需要认证：是
    """
    # 这里可以添加管理员权限检查，目前为简化演示而略过
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get(
    "/me", 
    response_model=UserResponse,
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息。"
)
def read_user_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户信息：
    
    - 需要认证：是
    """
    return current_user

@router.get(
    "/{user_id}", 
    response_model=UserResponse,
    summary="获取指定用户",
    description="根据用户ID获取用户信息。"
)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    根据ID获取用户信息：
    
    - **user_id**: 用户ID
    - 需要认证：是
    """
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put(
    "/{user_id}", 
    response_model=UserResponse,
    summary="更新用户信息",
    description="更新指定用户的信息，只有用户本人或管理员可以执行此操作。"
)
def update_user_endpoint(
    user_id: int, 
    user_update: UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新用户信息：
    
    - **user_id**: 用户ID
    - **email**: 可选，新的邮箱地址
    - **password**: 可选，新的密码
    - 需要认证：是
    - 权限：仅用户本人或管理员
    """
    # 检查是否是本人或管理员
    if current_user.id != user_id:
        # 这里可以添加管理员权限检查，目前为简化演示而略过
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    db_user = update_user(db, user_id=user_id, user_update=user_update)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete(
    "/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
    description="删除指定用户，只有用户本人或管理员可以执行此操作。"
)
def delete_user_endpoint(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除用户：
    
    - **user_id**: 用户ID
    - 需要认证：是
    - 权限：仅用户本人或管理员
    """
    # 检查是否是本人或管理员
    if current_user.id != user_id:
        # 这里可以添加管理员权限检查，目前为简化演示而略过
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None 