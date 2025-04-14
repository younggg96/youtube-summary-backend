from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from app.services.downloader import download_audio, DEFAULT_OUTPUT_DIR
from app.services.transcriber import transcribe_audio
from app.services.summarizer import summarize_text
import os
import logging
from dotenv import load_dotenv
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 音频文件清理配置
KEEP_AUDIO_FILES = os.getenv("KEEP_AUDIO_FILES", "false").lower() == "true"

router = APIRouter()

class VideoRequest(BaseModel):
    video_url: str
    keep_audio: bool = False  # 是否保留音频文件（覆盖全局配置）
    
    @field_validator('video_url')
    @classmethod
    def validate_youtube_url(cls, v):
        if not re.match(r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]+', v):
            raise ValueError('Invalid YouTube URL format')
        return v

@router.post("/summarize")
async def summarize_video(data: VideoRequest):
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
        summary = summarize_text(transcript)
        logger.info("Summary generated successfully")
        
        # 判断是否需要清理音频文件
        should_keep_audio = data.keep_audio or KEEP_AUDIO_FILES
        
        # 清理音频文件（如果配置为不保留）
        if not should_keep_audio and os.path.exists(audio_path):
            os.remove(audio_path)
            logger.info(f"Removed audio file: {audio_path}")
        elif should_keep_audio:
            logger.info(f"Keeping audio file: {audio_path}")
        
        return {"summary": summary}
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
