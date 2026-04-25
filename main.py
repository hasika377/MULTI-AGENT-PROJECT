"""
Gemini API Wrapper - FastAPI Backend
A simple API wrapper around Google's Gemini API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
from typing import Dict, Tuple, Optional

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Gemini API Wrapper",
    description="A simple FastAPI wrapper around Google's Gemini API",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# Configure Gemini API (only if not in debug mode)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY and not DEBUG_MODE:
    raise ValueError("GEMINI_API_KEY environment variable not set")

if not DEBUG_MODE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Rate limiting & Caching
RESPONSE_CACHE: Dict[str, Tuple[str, datetime]] = {}  # {prompt_hash: (response, timestamp)}
REQUEST_TIMES = []  # Track request times for rate limiting
RATE_LIMIT = 5  # Free tier: 5 requests per minute
RATE_LIMIT_WINDOW = 60  # seconds
CACHE_DURATION = 3600  # Cache responses for 1 hour

# Request/Response Models
class PromptRequest(BaseModel):
    prompt: str
    model: str = "gemini-2.5-flash"

class AIResponse(BaseModel):
    prompt: str
    response: str
    model: str

class HealthResponse(BaseModel):
    status: str
    message: str

# Helper Functions for Rate Limiting & Caching
def get_cache_key(prompt: str, model: str) -> str:
    """Generate cache key from prompt and model"""
    import hashlib
    return hashlib.md5(f"{prompt}_{model}".encode()).hexdigest()

def check_rate_limit() -> bool:
    """Check if we're within rate limit"""
    global REQUEST_TIMES
    now = time.time()
    # Remove old requests outside the window
    REQUEST_TIMES = [t for t in REQUEST_TIMES if now - t < RATE_LIMIT_WINDOW]
    return len(REQUEST_TIMES) < RATE_LIMIT

def record_request():
    """Record a new API request"""
    global REQUEST_TIMES
    REQUEST_TIMES.append(time.time())

def get_cached_response(cache_key: str) -> Optional[str]:
    """Retrieve cached response if available and not expired"""
    if cache_key in RESPONSE_CACHE:
        response, timestamp = RESPONSE_CACHE[cache_key]
        if datetime.now() - timestamp < timedelta(seconds=CACHE_DURATION):
            return response
        else:
            del RESPONSE_CACHE[cache_key]
    return None

def cache_response(cache_key: str, response: str):
    """Store response in cache"""
    RESPONSE_CACHE[cache_key] = (response, datetime.now())

# Mock Responses (for DEBUG mode - no API quota usage)
MOCK_RESPONSES = {
    "hello": "Hello! I'm Gemini running in mock mode. This is a fake response that costs no API quota. Perfect for development!",
    "who are you": "I'm Gemini, an AI assistant. Currently running in mock/debug mode, so I'm returning pre-written responses instead of calling the real API.",
    "what is python": "Python is a high-level programming language known for its simplicity and readability. It's widely used in web development, data science, AI, and automation.",
    "tell me a joke": "Why did the programmer quit his job? Because he didn't get arrays! 😄 (This is a mock response - no API calls used!)",
    "default": "This is a mock response from Gemini in DEBUG mode. No API quota was used! You can test the app without hitting the free tier limits."
}

def get_mock_response(prompt: str) -> str:
    """Generate a mock response based on prompt keywords"""
    prompt_lower = prompt.lower()
    for key, response in MOCK_RESPONSES.items():
        if key in prompt_lower:
            return response
    return MOCK_RESPONSES["default"]


# Health Check Endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the API is running"""
    return {
        "status": "healthy",
        "message": "Gemini API Wrapper is running"
    }

# Main Chat/Prompt Endpoint
@app.post("/chat", response_model=AIResponse)
async def chat(request: PromptRequest):
    """
    Send a prompt to Gemini and get a response
    
    - **prompt**: The text prompt to send to Gemini
    - **model**: The model to use (default: gemini-2.5-flash)
    """
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Check cache first (avoids quota usage)
        cache_key = get_cache_key(request.prompt, request.model)
        cached = get_cached_response(cache_key)
        if cached:
            return {
                "prompt": request.prompt,
                "response": cached + " [CACHED]",
                "model": request.model
            }
        
        # Check rate limit
        if not check_rate_limit():
            remaining = RATE_LIMIT_WINDOW - (time.time() - REQUEST_TIMES[0])
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limit exceeded. Free tier: {RATE_LIMIT} requests per {RATE_LIMIT_WINDOW}s. Please wait {remaining:.0f}s"
            )
        
        # Use mock response if in DEBUG mode (no API quota used)
        if DEBUG_MODE:
            response_text = get_mock_response(request.prompt)
            record_request()
            cache_response(cache_key, response_text)
            return {
                "prompt": request.prompt,
                "response": response_text + " [MOCK MODE - NO API QUOTA USED]",
                "model": request.model
            }
        
        # Initialize the model
        model = genai.GenerativeModel(request.model)
        
        # Generate response
        response = model.generate_content(request.prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="No response from Gemini API")
        
        # Record request and cache response
        record_request()
        cache_response(cache_key, response.text)
        
        return {
            "prompt": request.prompt,
            "response": response.text,
            "model": request.model
        }
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {str(e)}")

# Stream Response Endpoint (for long responses)
@app.post("/chat-stream")
async def chat_stream(request: PromptRequest):
    """
    Send a prompt to Gemini and stream the response
    """
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        model = genai.GenerativeModel(request.model)
        response = model.generate_content(request.prompt, stream=True)
        
        def response_generator():
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        
        return {
            "prompt": request.prompt,
            "model": request.model,
            "streaming": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {str(e)}")

# Root Endpoint
@app.get("/")
async def root():
    """API Documentation"""
    mode = "🔧 DEBUG MODE (Mock responses - no API quota)" if DEBUG_MODE else "🚀 PRODUCTION (Real Gemini API)"
    return {
        "name": "Gemini API Wrapper",
        "version": "1.0.0",
        "mode": mode,
        "endpoints": {
            "GET /health": "Check API health",
            "POST /chat": "Send prompt and get response",
            "POST /chat-stream": "Send prompt and stream response",
            "GET /stats": "View cache and rate limit stats",
            "GET /docs": "Interactive API documentation (Swagger UI)",
            "GET /redoc": "ReDoc documentation"
        }
    }

# Cache & Rate Limit Stats
@app.get("/stats")
async def get_stats():
    """Get cache and rate limit statistics"""
    now = time.time()
    recent_requests = len([t for t in REQUEST_TIMES if now - t < RATE_LIMIT_WINDOW])
    return {
        "cache_size": len(RESPONSE_CACHE),
        "requests_this_minute": recent_requests,
        "rate_limit": RATE_LIMIT,
        "requests_remaining": max(0, RATE_LIMIT - recent_requests),
        "cache_items": list(RESPONSE_CACHE.keys()) if RESPONSE_CACHE else []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
