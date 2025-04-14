import os
import time
import random
import subprocess
import yt_dlp
import re
import uuid
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# 从环境变量获取默认输出目录，如果没有设置则使用当前目录
DEFAULT_OUTPUT_DIR = os.getenv("AUDIO_OUTPUT_DIR", ".")

def download_with_ytdlp(url: str, output_dir: str = None) -> str:
    """
    使用 yt-dlp 下载音频文件
    
    Args:
        url: YouTube 视频 URL
        output_dir: 输出目录，如果为 None 则使用环境变量中的配置
        
    Returns:
        str: 下载的音频文件路径
        
    Raises:
        FileNotFoundError: 如果输出目录不存在或无法创建
        PermissionError: 如果没有写入权限
        Exception: 其他下载错误
    """
    try:
        # 获取输出目录
        if output_dir is None:
            output_dir = os.getenv('AUDIO_OUTPUT_DIR', '/app/downloaded_audio')
        
        # 确保输出目录存在
        output_path = Path(output_dir)
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")
            except PermissionError:
                logger.error(f"Permission denied when creating directory: {output_dir}")
                raise PermissionError(f"无法创建目录 {output_dir}，请检查权限")
            except Exception as e:
                logger.error(f"Failed to create directory {output_dir}: {str(e)}")
                raise FileNotFoundError(f"无法创建输出目录: {output_dir}")
        
        # 检查目录权限
        if not os.access(output_dir, os.W_OK):
            logger.error(f"No write permission for directory: {output_dir}")
            raise PermissionError(f"没有目录 {output_dir} 的写入权限")
        
        # 配置下载选项
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        # 下载音频
        logger.info(f"Starting download from URL: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            output_file = os.path.join(output_dir, f"{video_id}.mp3")
            
            if not os.path.exists(output_file):
                logger.error(f"Downloaded file not found: {output_file}")
                raise FileNotFoundError(f"下载文件未找到: {output_file}")
            
            logger.info(f"Successfully downloaded audio to: {output_file}")
            return output_file
            
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"YouTube download error: {str(e)}")
        raise Exception(f"YouTube 下载错误: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during download: {str(e)}")
        raise Exception(f"下载过程中发生错误: {str(e)}")

def download_audio(video_url: str, output_path: str = None, filename: str = None) -> str:
    """
    下载YouTube视频的音频部分
    
    Args:
        video_url: YouTube视频链接
        output_path: 音频文件保存路径
        filename: 音频文件名，默认使用唯一ID生成
    
    Returns:
        音频文件的完整路径
    """
    try:
        # 如果没有提供输出路径，使用默认路径
        if output_path is None:
            output_path = DEFAULT_OUTPUT_DIR
            
        # 如果没有提供文件名，则使用唯一ID生成安全的文件名
        if not filename:
            filename = f"audio_{uuid.uuid4().hex[:8]}.mp4"
            
        # 使用 yt-dlp 下载
        return download_with_ytdlp(video_url, output_path)
        
    except Exception as e:
        logger.error(f"All download methods failed: {str(e)}")
        raise Exception(f"Failed to download audio: {str(e)}")
