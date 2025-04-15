from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, field_validator, Field
from app.services.downloader import download_audio, DEFAULT_OUTPUT_DIR
from app.services.transcriber import transcribe_audio
from app.services.summarizer import summarize_text
from app.services.youtube_search import search_channel_videos
from app.database.base import get_db
from app.models.user import User
from app.auth.security import get_current_user
from app.schemas.summary import SummaryCreate, SummaryResponse, SummaryUpdate
from app.crud.summary import (
    create_summary, 
    get_summary, 
    get_summaries, 
    get_user_summaries,
    update_summary,
    delete_summary,
    extract_video_id
)
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import logging
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 音频文件清理配置
KEEP_AUDIO_FILES = os.getenv("KEEP_AUDIO_FILES", "false").lower() == "true"

# 创建路由，使用明确的标签和前缀
router = APIRouter(
    prefix="/videos",
    tags=["videos"],
    responses={404: {"description": "未找到资源"}}
)

class VideoRequest(BaseModel):
    video_url: str = Field(..., description="YouTube视频URL", example="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    keep_audio: bool = Field(False, description="是否保留音频文件（覆盖全局配置）")
    
    @field_validator('video_url')
    @classmethod
    def validate_youtube_url(cls, v):
        if not re.match(r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+', v):
            raise ValueError('Invalid YouTube URL format')
        return v

class ChannelRequest(BaseModel):
    channel_name: str = Field(..., description="YouTube频道名称", example="Google Developers")
    max_results: int = Field(20, description="最大结果数，默认20个")

@router.post(
    "/summarize",
    response_model=SummaryResponse,
    summary="生成视频摘要",
    description="根据YouTube视频URL生成内容摘要"
)
async def summarize_video(
    data: VideoRequest, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    生成YouTube视频摘要：
    
    - **video_url**: YouTube视频URL
    - **keep_audio**: 是否保留下载的音频文件
    
    返回视频摘要信息，包括转录文本和摘要内容。
    """
    try:
        logger.info(f"Processing video URL: {data.video_url}")
        
        # 下载音频
        logger.info(f"Downloading audio to {DEFAULT_OUTPUT_DIR}...")
        audio_path = download_audio(data.video_url)
        logger.info(f"Audio downloaded to: {audio_path}")
        
        # 转录音频
        logger.info("Transcribing audio...")
        transcript = transcribe_audio(audio_path)
        logger.info(f"Transcription completed, length: {len(transcript)} characters")
        
        # 生成摘要
        logger.info("Generating summary...")
        summary_text = summarize_text(transcript)
        logger.info("Summary generated successfully")
        
        # 判断是否需要清理音频文件
        should_keep_audio = data.keep_audio or KEEP_AUDIO_FILES
        audio_file_path = None
        
        if should_keep_audio:
            audio_file_path = audio_path
            logger.info(f"Keeping audio file: {audio_path}")
        else:
            # 清理音频文件
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.info(f"Removed audio file: {audio_path}")
        
        # 获取视频ID，用于存储在数据库中
        video_id = extract_video_id(data.video_url)
        
        # 创建数据库记录
        summary_data = SummaryCreate(
            video_url=data.video_url,
            keep_audio=should_keep_audio,
            # 可以添加更多元数据，如标题和频道名
        )
        
        # 创建摘要记录
        user_id = current_user.id if current_user else None
        db_summary = create_summary(db, summary_data, user_id)
        
        # 更新摘要内容和转录
        update_data = SummaryUpdate(
            transcript=transcript,
            summary=summary_text
        )
        db_summary = update_summary(db, db_summary.id, update_data)
        
        return db_summary
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/",
    response_model=List[SummaryResponse],
    summary="获取所有摘要",
    description="获取所有视频摘要列表"
)
def read_summaries(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """获取所有视频摘要列表"""
    summaries = get_summaries(db, skip=skip, limit=limit)
    return summaries

@router.get(
    "/my",
    response_model=List[SummaryResponse],
    summary="获取我的摘要",
    description="获取当前用户的视频摘要列表"
)
def read_my_summaries(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的视频摘要列表"""
    summaries = get_user_summaries(db, current_user.id, skip=skip, limit=limit)
    return summaries

@router.get(
    "/{summary_id}",
    response_model=SummaryResponse,
    summary="获取特定摘要",
    description="获取特定视频摘要的详细信息"
)
def read_summary(
    summary_id: int, 
    db: Session = Depends(get_db)
):
    """获取特定视频摘要"""
    db_summary = get_summary(db, summary_id=summary_id)
    if db_summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    return db_summary

@router.delete(
    "/{summary_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除摘要",
    description="删除特定视频摘要"
)
def delete_summary_endpoint(
    summary_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除视频摘要"""
    db_summary = get_summary(db, summary_id=summary_id)
    if db_summary is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    # 检查权限
    if db_summary.user_id and db_summary.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this summary"
        )
    
    success = delete_summary(db, summary_id=summary_id)
    if not success:
        raise HTTPException(status_code=404, detail="Summary not found")
    return None

@router.post(
    "/search_channel",
    summary="搜索频道视频",
    description="搜索YouTube频道的视频列表并按上传时间排序"
)
async def search_channel(data: ChannelRequest) -> Dict[str, Any]:
    """
    搜索YouTube博主/频道的视频列表并按上传时间排序
    
    - **channel_name**: YouTube频道名称
    - **max_results**: 返回的最大结果数
    """
    try:
        logger.info(f"Searching videos for channel: {data.channel_name}")
        
        # 调用服务获取视频列表
        videos = search_channel_videos(data.channel_name, data.max_results)
        
        # 返回结果
        return {
            "channel_name": data.channel_name,
            "video_count": len(videos),
            "videos": videos
        }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching channel: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
