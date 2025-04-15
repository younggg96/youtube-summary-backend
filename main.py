from fastapi import FastAPI
from app.api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from app.database.base import engine
from app.models import User, VideoSummary  # 导入所有模型，以便创建表
import os
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 创建所有表
User.metadata.create_all(bind=engine)
VideoSummary.metadata.create_all(bind=engine)

# 创建FastAPI应用，添加更详细的API文档配置
app = FastAPI(
    title="YouTube Summary API",
    description="API for summarizing YouTube videos with user management and authentication",
    version="1.0.0",
    openapi_url="/openapi.json",  # 使用根路径的OpenAPI架构URL
    docs_url="/docs",  # Swagger UI路径
    redoc_url="/redoc",  # ReDoc路径
)

# 添加CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的前端域名而不是"*"
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 包含API路由
app.include_router(api_router)

# 定义根路由
@app.get("/")
def read_root():
    logger.debug("访问根路径")
    return {"message": "YouTube Summary API is running"}
