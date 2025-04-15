# Docker 部署指南

本文档介绍了如何使用 Docker 部署 YouTube 视频摘要服务。

## 前提条件

* 安装 [Docker](https://docs.docker.com/get-docker/)
* 安装 [Docker Compose](https://docs.docker.com/compose/install/)
* 获取 OpenAI API 密钥

## 部署步骤

### 1. 准备环境变量

创建 `.env` 文件并添加你的 OpenAI API 密钥：

```bash
# 手动创建
echo "OPENAI_API_KEY=你的API密钥" > .env
```

### 2. 构建并启动 Docker 容器

```bash
docker-compose up -d
```

这会在后台启动服务，API 将在 `http://localhost:8000` 上可用。

### 3. 检查服务状态

```bash
docker-compose ps
```

### 4. 查看日志

```bash
docker-compose logs -f
```

## API 使用

部署完成后，你可以使用以下 curl 命令来测试 API：

```bash
curl -X POST "http://localhost:8000/summarize" \
     -H "Content-Type: application/json" \
     -d '{"video_url": "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"}'
```

或者访问 Swagger 文档：http://localhost:8000/docs

## 停止服务

```bash
docker-compose down
```

## 更新服务

如果你更新了代码，可以按照以下步骤重新构建和部署服务：

```bash
# 停止当前服务
docker-compose down

# 重新构建镜像
docker-compose build

# 启动新服务
docker-compose up -d
```

## 存储配置

默认情况下，API 不会永久保存下载的音频文件。如果你想保存这些文件，请编辑 `docker-compose.yml` 文件，取消注释以下部分：

```yaml
volumes:
  - ./downloaded_audio:/app/downloaded_audio
```

并确保你已经修改了代码，将音频文件保存到 `/app/downloaded_audio` 目录中。 