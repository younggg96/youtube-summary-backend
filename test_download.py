import os
from app.services.downloader import download_with_ytdlp

def test_download():
    # 创建下载目录
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    
    # 测试下载
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 使用一个示例视频
    try:
        file_path = download_with_ytdlp(url, output_dir)
        print(f"下载成功：{file_path}")
    except Exception as e:
        print(f"下载失败：{str(e)}")

if __name__ == "__main__":
    test_download() 