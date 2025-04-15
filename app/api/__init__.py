from fastapi import APIRouter
from app.api.summary import router as summary_router
from app.api.user import router as user_router
from app.api.auth import router as auth_router

# 创建主路由，确保在docs中显示
router = APIRouter(prefix="/api")

# 包含子路由，设置tags确保在docs中正确分类
router.include_router(summary_router)
router.include_router(user_router)
router.include_router(auth_router)

__all__ = ["router"] 