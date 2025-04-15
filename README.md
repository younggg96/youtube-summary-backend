# YouTube Summary Backend

This project is a backend service for summarizing YouTube videos.

## Features
- YouTube video data fetching
- Video content summarization
- API endpoints for client applications
- User authentication and account management
- Database storage for video summaries and user data

## Setup

### Prerequisites
- Python 3.8+
- FFmpeg (for audio processing)
- PostgreSQL (optional, SQLite is used by default)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/youtube-summary-backend.git
cd youtube-summary-backend
```

2. Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` file and configure your environment variables
```
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
DATABASE_URL=sqlite:///./youtube_summary.db
# For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost/youtube_summary

# JWT Authentication
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

5. Run database migrations
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

6. Start the development server
```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Management

### Creating Migrations
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations
```bash
alembic upgrade head
```

### Reverting Migrations
```bash
alembic downgrade -1  # Revert the last migration
```

## API Endpoints

### Authentication
- `POST /api/auth/token` - Login and obtain JWT token

### Users
- `POST /api/users/` - Register a new user
- `GET /api/users/me` - Get current user information
- `PUT /api/users/{user_id}` - Update user information
- `DELETE /api/users/{user_id}` - Delete user account

### Video Summaries
- `POST /api/videos/summarize` - Generate summary for a YouTube video
- `GET /api/videos/` - Get all video summaries
- `GET /api/videos/my` - Get summaries created by the current user
- `GET /api/videos/{summary_id}` - Get a specific video summary
- `DELETE /api/videos/{summary_id}` - Delete a video summary

### YouTube Channel Search
- `POST /api/videos/search_channel` - Search videos from a YouTube channel 