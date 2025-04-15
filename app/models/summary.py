from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class VideoSummary(Base):
    __tablename__ = "video_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String, index=True, nullable=False)  # YouTube视频ID
    video_url = Column(String, nullable=False)
    video_title = Column(String)
    channel_name = Column(String)
    transcript = Column(Text)  # 完整转录
    summary = Column(Text)  # 生成的摘要
    audio_path = Column(String, nullable=True)  # 音频文件路径（如果保存）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 外键关联到用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 与User的关系
    user = relationship("User", back_populates="summaries") 