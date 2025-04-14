import whisper
import os
import logging

logger = logging.getLogger(__name__)

# 从环境变量获取 Whisper 模型大小
DEFAULT_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")

def transcribe_audio(audio_path: str, model_size: str = None) -> str:
    """
    使用 Whisper 模型转录音频文件
    
    Args:
        audio_path: 音频文件路径
        model_size: Whisper 模型大小 (tiny, base, small, medium, large)
    
    Returns:
        转录后的文本
    """
    try:
        # 如果没有指定模型大小，使用默认模型大小
        if model_size is None:
            model_size = DEFAULT_MODEL_SIZE
            
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found at: {audio_path}")
            
        logger.info(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        
        logger.info(f"Transcribing audio file: {audio_path}")
        result = model.transcribe(audio_path, language='zh')
        
        if not result or "text" not in result:
            raise ValueError("Transcription failed: No text output")
            
        transcript = result["text"]
        logger.info(f"Transcription completed. Length: {len(transcript)} characters")
        
        return transcript
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise Exception(f"Failed to load audio: {str(e)}")
