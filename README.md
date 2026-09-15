# Next-Level Sentiment Analysis API

An enterprise-ready FastAPI application that uses a pre-trained Hugging Face transformer model to classify text into positive, negative, or neutral sentiment with confidence scores.

## Upgrades & Features in V2
- **API Key Authentication**: Secure endpoints using the `X-API-Key` header.
- **LRU Caching**: Saves compute and heavily speeds up requests for duplicate texts.
- **CORS Middleware**: Ready to be consumed by web frontends out-of-the-box.
- **Logging Middleware**: Automatically tracks request timing and API health.
- **Pydantic Validation**: Strict limits on text lengths and batch sizes to prevent memory overflow.
- **Docker Ready**: Pre-packaged `Dockerfile` that caches the ML model inside the image for fast scaling.
- **Lifespan Context**: Elegant model loading on startup and cleanup on shutdown.

## Setup Instructions

### Option A: Using Docker (Recommended)
1. Build the image (this will download the model weights during the build process):
   ```bash
   docker build -t sentiment-api .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 sentiment-api
   ```

### Option B: Using Python Virtual Environment
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the API server:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

### Authentication
Both `/api/analyze` and `/api/analyze/batch` require an API Key.
Header: `X-API-Key: super-secret-key`

*(Note: Change `API_KEY` in `main.py` or use environment variables for production).*

### 1. Health Check (`GET /`)
Public endpoint to check if the server is healthy and the model is loaded in memory.

### 2. Analyze Single Text (`POST /api/analyze`)

**Request**:
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: super-secret-key" \
  -d '{"text": "I absolutely love this new feature!"}'
```

### 3. Analyze Batch (`POST /api/analyze/batch`)
Allows up to 10 texts per request.

**Request**:
```bash
curl -X POST http://localhost:8000/api/analyze/batch \
  -H "Content-Type: application/json" \
  -H "X-API-Key: super-secret-key" \
  -d '{"texts": ["The movie was fantastic!", "The service was terrible.", "It was okay, nothing special."]}'
```
