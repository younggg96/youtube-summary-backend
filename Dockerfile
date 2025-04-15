FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY .env .
COPY main.py .
COPY app/ app/

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建下载目录并设置权限
RUN mkdir -p /app/downloaded_audio && \
    chmod 777 /app/downloaded_audio

# 暴露端口
EXPOSE 8000

# 启动命令由 docker-compose.yml 提供 