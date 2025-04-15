from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re

class SummaryBase(BaseModel):
    video_url: str
    
    @field_validator('video_url')
    def validate_youtube_url(cls, v):
        if not re.match(r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+', v):
            raise ValueError('Invalid YouTube URL format')
        return v

class SummaryCreate(SummaryBase):
    keep_audio: bool = False
    video_title: Optional[str] = None
    channel_name: Optional[str] = None

class SummaryUpdate(BaseModel):
    summary: Optional[str] = None
    transcript: Optional[str] = None

class SummaryResponse(SummaryBase):
    id: int
    video_id: str
    video_title: Optional[str] = None
    channel_name: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_id: Optional[int] = None
    
    class Config:
        from_attributes = True 