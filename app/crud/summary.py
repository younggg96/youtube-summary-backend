from sqlalchemy.orm import Session
from app.models.summary import VideoSummary
from app.schemas.summary import SummaryCreate, SummaryUpdate
from typing import List, Optional
import re

def extract_video_id(url: str) -> str:
    """从YouTube URL中提取视频ID"""
    pattern = r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return ""

def create_summary(db: Session, summary: SummaryCreate, user_id: Optional[int] = None) -> VideoSummary:
    """创建新的视频摘要"""
    video_id = extract_video_id(summary.video_url)
    db_summary = VideoSummary(
        video_id=video_id,
        video_url=summary.video_url,
        video_title=summary.video_title,
        channel_name=summary.channel_name,
        user_id=user_id
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

def get_summary(db: Session, summary_id: int) -> VideoSummary:
    """根据ID获取视频摘要"""
    return db.query(VideoSummary).filter(VideoSummary.id == summary_id).first()

def get_summary_by_video_id(db: Session, video_id: str) -> VideoSummary:
    """根据视频ID获取摘要"""
    return db.query(VideoSummary).filter(VideoSummary.video_id == video_id).first()

def get_summaries(db: Session, skip: int = 0, limit: int = 100) -> List[VideoSummary]:
    """获取所有视频摘要"""
    return db.query(VideoSummary).order_by(VideoSummary.created_at.desc()).offset(skip).limit(limit).all()

def get_user_summaries(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[VideoSummary]:
    """获取指定用户的所有视频摘要"""
    return db.query(VideoSummary).filter(VideoSummary.user_id == user_id).order_by(VideoSummary.created_at.desc()).offset(skip).limit(limit).all()

def update_summary(db: Session, summary_id: int, summary_update: SummaryUpdate) -> VideoSummary:
    """更新视频摘要"""
    db_summary = get_summary(db, summary_id)
    if not db_summary:
        return None
    
    update_data = summary_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_summary, key, value)
    
    db.commit()
    db.refresh(db_summary)
    return db_summary

def delete_summary(db: Session, summary_id: int) -> bool:
    """删除视频摘要"""
    db_summary = get_summary(db, summary_id)
    if not db_summary:
        return False
    
    db.delete(db_summary)
    db.commit()
    return True 