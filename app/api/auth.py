from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.base import get_db
from app.schemas.user import Token
from app.crud import authenticate_user
from app.auth.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# 创建认证路由，添加详细描述
router = APIRouter(
    prefix="/auth", 
    tags=["authentication"],
    responses={401: {"description": "认证失败"}}
)

@router.post(
    "/token", 
    response_model=Token,
    summary="登录获取令牌",
    description="使用用户名和密码登录，获取JWT访问令牌。"
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录获取JWT令牌：
    
    - **username**: 用户名
    - **password**: 密码
    
    返回:
    - **access_token**: JWT访问令牌
    - **token_type**: 令牌类型 (bearer)
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 