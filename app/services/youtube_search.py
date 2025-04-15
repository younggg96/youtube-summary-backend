import os
import logging
from typing import List, Dict, Any
import yt_dlp
from datetime import datetime
import re

logger = logging.getLogger(__name__)

def search_channel_videos(channel_name: str, max_results: int = 20) -> List[Dict[Any, Any]]:
    """
    搜索特定YouTube博主/频道的视频列表并按上传时间排序
    
    Args:
        channel_name: YouTube博主名字或频道名称
        max_results: 最大返回结果数量，默认20
        
    Returns:
        List[Dict]: 包含视频信息的列表，按上传日期降序排序
    """
    try:
        logger.info(f"Searching videos for channel: {channel_name}")
        
        # 检查是否已经是一个YouTube频道链接
        channel_url_pattern = re.compile(r'(https?://)?(www\.)?youtube\.com/(@|channel/|c/|user/)?([^/\s]+)')
        channel_match = channel_url_pattern.match(channel_name)
        
        if channel_match:
            # 已经是频道链接，直接使用
            logger.info(f"Input appears to be a channel URL: {channel_name}")
            channel_url = channel_name
            if not channel_name.startswith('http'):
                channel_url = f"https://{channel_name}"
        else:
            # 使用搜索功能查找频道
            logger.info(f"Searching for channel: {channel_name}")
            
            ydl_opts_search = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': False,  # 修改为False
                'ignoreerrors': True,
                'skip_download': True,
            }
            
            # 构建搜索查询
            search_query = f"ytsearch:{channel_name} channel"
            
            try:
                # 搜索频道
                with yt_dlp.YoutubeDL(ydl_opts_search) as ydl:
                    search_results = ydl.extract_info(search_query, download=False)
                    
                    if not search_results or 'entries' not in search_results or not search_results['entries']:
                        logger.warning(f"No channel found for: {channel_name}")
                        return []
                    
                    # 尝试找到匹配的频道
                    channel_url = None
                    for entry in search_results['entries']:
                        # 检查是否为频道
                        if 'url' in entry and ('youtube.com/@' in entry['url'] or 
                                              'youtube.com/channel/' in entry['url'] or
                                              'youtube.com/c/' in entry['url'] or
                                              'youtube.com/user/' in entry['url']):
                            channel_url = entry['url']
                            logger.info(f"Found channel URL: {channel_url}")
                            break
                    
                    if not channel_url:
                        # 尝试使用第一个结果对应的频道
                        if 'uploader_url' in search_results['entries'][0]:
                            channel_url = search_results['entries'][0]['uploader_url']
                            logger.info(f"Using uploader URL as channel: {channel_url}")
                        else:
                            logger.warning(f"Could not find channel URL for: {channel_name}")
                            return []
            except Exception as e:
                logger.error(f"Error during channel search: {str(e)}")
                # 尝试直接构建可能的频道URL
                channel_url = f"https://www.youtube.com/@{channel_name.replace(' ', '')}"
                logger.info(f"Attempting with constructed URL: {channel_url}")
        
        # 获取频道的视频
        logger.info(f"Fetching videos from channel: {channel_url}")
        
        ydl_opts_videos = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'extract_flat': True,
            'skip_download': True,
            'playlistend': max_results
        }
        
        try:
            # 获取频道上传的视频列表
            with yt_dlp.YoutubeDL(ydl_opts_videos) as ydl_videos:
                # 添加 /videos 以获取上传的视频列表
                if not channel_url.endswith('/videos'):
                    playlist_url = f"{channel_url}/videos"
                else:
                    playlist_url = channel_url
                
                logger.info(f"Fetching videos from: {playlist_url}")
                channel_info = ydl_videos.extract_info(playlist_url, download=False)
                
                if not channel_info or 'entries' not in channel_info:
                    logger.warning(f"No videos found for channel: {channel_url}")
                    # 尝试一个备选方案
                    if '@' in channel_url:
                        # 尝试移除@符号
                        alt_url = channel_url.replace('@', 'c/')
                        logger.info(f"Trying alternative URL: {alt_url}/videos")
                        channel_info = ydl_videos.extract_info(f"{alt_url}/videos", download=False)
                    
                    if not channel_info or 'entries' not in channel_info:
                        logger.warning(f"Alternative attempt also failed")
                        return []
                
                # 处理视频信息
                videos = []
                for video in channel_info.get('entries', []):
                    if not video:
                        continue
                    
                    # 解析上传日期
                    upload_date = video.get('upload_date', '')
                    if upload_date and len(upload_date) == 8:
                        try:
                            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                        except Exception:
                            formatted_date = ""
                    else:
                        formatted_date = ""
                    
                    # 构建视频信息对象
                    video_info = {
                        'id': video.get('id', ''),
                        'title': video.get('title', ''),
                        'url': f"https://www.youtube.com/watch?v={video.get('id', '')}",
                        'upload_date': formatted_date,
                        'duration': video.get('duration', 0),
                        'view_count': video.get('view_count', 0),
                        'description': video.get('description', '')
                    }
                    videos.append(video_info)
                
                # 按上传日期排序（降序）
                videos.sort(key=lambda x: x['upload_date'], reverse=True)
                
                logger.info(f"Found {len(videos)} videos for channel: {channel_name}")
                return videos
        
        except Exception as e:
            logger.error(f"Error fetching channel videos: {str(e)}")
            # 最后的尝试：直接使用频道名称作为关键词搜索视频
            try:
                logger.info(f"Trying direct video search for: {channel_name}")
                search_query = f"ytsearch{max_results}:{channel_name}"
                
                with yt_dlp.YoutubeDL(ydl_opts_videos) as ydl_direct:
                    search_results = ydl_direct.extract_info(search_query, download=False)
                    
                    if not search_results or 'entries' not in search_results:
                        return []
                    
                    videos = []
                    for video in search_results.get('entries', []):
                        if not video:
                            continue
                        
                        # 过滤掉不是指定频道的视频
                        video_uploader = video.get('uploader', '').lower()
                        if channel_name.lower() not in video_uploader:
                            continue
                        
                        # 解析上传日期
                        upload_date = video.get('upload_date', '')
                        if upload_date and len(upload_date) == 8:
                            try:
                                formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                            except Exception:
                                formatted_date = ""
                        else:
                            formatted_date = ""
                        
                        # 构建视频信息对象
                        video_info = {
                            'id': video.get('id', ''),
                            'title': video.get('title', ''),
                            'url': f"https://www.youtube.com/watch?v={video.get('id', '')}",
                            'upload_date': formatted_date,
                            'duration': video.get('duration', 0),
                            'view_count': video.get('view_count', 0),
                            'description': video.get('description', '')
                        }
                        videos.append(video_info)
                    
                    # 按上传日期排序（降序）
                    videos.sort(key=lambda x: x['upload_date'], reverse=True)
                    
                    logger.info(f"Found {len(videos)} videos via direct search for: {channel_name}")
                    return videos
            except Exception as direct_error:
                logger.error(f"Direct video search also failed: {str(direct_error)}")
                return []
                
    except Exception as e:
        logger.error(f"Error searching YouTube channel: {str(e)}")
        raise Exception(f"搜索YouTube频道时出错: {str(e)}") 