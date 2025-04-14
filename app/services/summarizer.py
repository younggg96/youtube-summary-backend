import openai
import os
import logging
from openai import OpenAI
import re

logger = logging.getLogger(__name__)

# 从环境变量获取 OpenAI 模型
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo-1106")

def chunk_text(text, max_chunk_size=4000):
    """
    将长文本分割成更小的块
    
    Args:
        text: 要分割的文本
        max_chunk_size: 每个块的最大字符数
    
    Returns:
        文本块列表
    """
    # 按句子分割
    sentences = re.split(r'(?<=[。！？.!?])\s*', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def summarize_text(text: str, model: str = None) -> str:
    """
    使用 OpenAI 模型总结文本
    
    Args:
        text: 要总结的文本
        model: OpenAI 模型名称
    
    Returns:
        总结后的文本
    """
    try:
        # 如果没有指定模型，使用默认模型
        if model is None:
            model = DEFAULT_MODEL
            
        # 获取 API 密钥
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 环境变量未设置")
        
        # 初始化客户端
        client = OpenAI(api_key=api_key)
        
        logger.info(f"Preparing text for summarization. Text length: {len(text)}")
        
        # 处理长文本
        if len(text) > 4000:
            logger.info("Text too long, chunking...")
            chunks = chunk_text(text)
            logger.info(f"Split into {len(chunks)} chunks")
            
            # 对每个块进行摘要
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Summarizing chunk {i+1}/{len(chunks)}")
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "你是一个擅长总结中文视频内容的助手。请简要总结以下文本片段。"},
                        {"role": "user", "content": f"请总结以下视频内容片段：\n{chunk}"}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                
                chunk_summary = response.choices[0].message.content
                chunk_summaries.append(chunk_summary)
            
            # 合并所有摘要
            combined_summary = "\n\n".join(chunk_summaries)
            
            # 对合并的摘要再进行一次总结
            logger.info("Creating final summary from chunk summaries")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个擅长总结中文视频内容的助手。请将以下多段摘要整合成一个连贯的整体摘要。"},
                    {"role": "user", "content": f"请把内容得到的文字生成一段可读性高的文字，不需要对文字进行总结，只需要把文字转换成可读性高的文字， 修改文章中的错别字，有语言不通的地方，请修改：\n\n{combined_summary}"}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            final_summary = response.choices[0].message.content
            logger.info(f"Final summary created, length: {len(final_summary)}")
            
            return final_summary
        else:
            # 对于较短的文本直接总结
            logger.info("Text within limits, summarizing directly")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个擅长中文视频内容的助手。"},
                    {"role": "user", "content": f"请把内容得到的文字生成一段可读性高的文字，不需要对文字进行总结，只需要把文字转换成可读性高的文字， 修改文章中的错别字，有语言不通的地方，请修改：\n\n{text}"}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            summary = response.choices[0].message.content
            logger.info(f"Summary created, length: {len(summary)}")
            
            return summary
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise Exception(f"Failed to summarize text: {str(e)}")
