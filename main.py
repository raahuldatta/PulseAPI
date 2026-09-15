import logging
import time
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from transformers import pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("sentiment_api")

# Constants
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
API_KEY = "super-secret-key"  # In production, load this from environment variables
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=403, detail="Could not validate API KEY"
        )
    return api_key_header

# Global model variable
sentiment_pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model on startup
    global sentiment_pipeline
    logger.info(f"Loading model '{MODEL_NAME}'... This might take a moment.")
    try:
        sentiment_pipeline = pipeline("sentiment-analysis", model=MODEL_NAME, top_k=None)
        logger.info("Model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        sentiment_pipeline = None
    yield
    # Clean up on shutdown
    logger.info("Shutting down API...")
    sentiment_pipeline = None

app = FastAPI(
    title="Next-Level Sentiment Analysis API",
    description="An enterprise-ready sentiment analysis API with caching, authentication, and logging.",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request timing logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - {process_time:.4f}s")
    return response

# Pydantic Models with Validation
class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Text to analyze")

class BatchTextRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=10, description="List of texts to analyze (max 10)")

class ClassScore(BaseModel):
    label: str
    score: float

class SentimentResponse(BaseModel):
    label: str
    confidence: float
    scores: list[ClassScore]

# LRU Cache for predicting text to save compute on repeated texts
@lru_cache(maxsize=1000)
def predict_text(text: str):
    if not sentiment_pipeline:
        raise RuntimeError("Model not initialized")
    return sentiment_pipeline(text)

def process_result(result) -> SentimentResponse:
    max_score = -1.0
    best_label = ""
    scores = []
    
    for score_dict in result:
        label = score_dict['label'].lower()
        score = float(score_dict['score'])
        scores.append(ClassScore(label=label, score=score))
        if score > max_score:
            max_score = score
            best_label = label
            
    return SentimentResponse(
        label=best_label,
        confidence=max_score,
        scores=scores
    )

@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": sentiment_pipeline is not None,
        "message": "Next-Level Sentiment Analysis API is running."
    }

@app.post("/api/analyze", response_model=SentimentResponse, tags=["Analysis"])
async def analyze_text(request: TextRequest, api_key: str = Security(get_api_key)):
    if not sentiment_pipeline:
        raise HTTPException(status_code=503, detail="Model is currently unavailable")
        
    try:
        results = predict_text(request.text)
        return process_result(results)
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")

@app.post("/api/analyze/batch", response_model=list[SentimentResponse], tags=["Analysis"])
async def analyze_batch(request: BatchTextRequest, api_key: str = Security(get_api_key)):
    if not sentiment_pipeline:
        raise HTTPException(status_code=503, detail="Model is currently unavailable")
        
    try:
        responses = []
        for text in request.texts:
            # Using our cached predict function for each text in the batch
            res = predict_text(text)
            responses.append(process_result(res))
        return responses
    except Exception as e:
        logger.error(f"Error during batch analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error")
