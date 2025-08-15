from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
import uvicorn
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up FastAPI application...")
    # TODO: Initialize database connections, cache, etc.
    # Create database tables
    from app.models import engine, Base
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    # TODO: Close database connections, cleanup resources, etc.

# Create FastAPI app instance
app = FastAPI(
    title="Ticket Orchestration Chat API",
    description="BestEgg Support Ticket Orchestration Chat",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server (Create React App)
        "http://localhost:3090",  # Your Vite dev server (actual port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3090",
        # Add your production frontend URLs here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this properly for production
)

# Import response utilities for global exception handlers
from app.utils.response_utils import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)

# Register global exception handlers from response_utils.py to standardize responses
app.add_exception_handler(Exception, general_exception_handler) # For general exceptions (Code 500) 
app.add_exception_handler(HTTPException, http_exception_handler) # For HTTP errors (Code 400, 401, 403, 404, 500)
app.add_exception_handler(RequestValidationError, validation_exception_handler) # For validation errors (Code 422)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "FastAPI backend is running"}

# Root endpoint - removed to avoid conflict with catch-all route

# API info endpoint
@app.get("/api/info")
async def api_info():
    return {
        "name": "LibreChat API",
        "version": "1.0.0",
        "description": "FastAPI backend for LibreChat",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Import and include route modules
from app.routes import auth, config, endpoints, user, conversations, models, files, messages, memory, stubs

# Register all API routes
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(config.router, prefix="/api", tags=["Configuration"])
app.include_router(endpoints.router, prefix="/api", tags=["Endpoints"])
app.include_router(user.router, prefix="/api", tags=["Users"])
app.include_router(conversations.router, prefix="/api/convos", tags=["Conversations"])
app.include_router(models.router, prefix="/api", tags=["Models"])
app.include_router(files.router, prefix="/api", tags=["Files"])
app.include_router(messages.router, prefix="/api/convos", tags=["Messages"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(stubs.router, prefix="/api", tags=["Stubs"])

# TODO: Import and include route modules here
# from app.routes import auth, users, conversations, messages, agents, assistants
# app.include_router(auth.router, prefix="/api", tags=["Authentication"])
# app.include_router(users.router, prefix="/api", tags=["Users"])
# app.include_router(conversations.router, prefix="/api", tags=["Conversations"])
# app.include_router(messages.router, prefix="/api", tags=["Messages"])
# app.include_router(agents.router, prefix="/api", tags=["Agents"])
# app.include_router(assistants.router, prefix="/api", tags=["Assistants"])

# Note: Static files are now handled by the catch-all route below

# Catch-all route to serve the frontend and static files
@app.get("/{full_path:path}")
async def catch_all(full_path: str, request: Request):
    """Catch-all route to serve the frontend for any path that doesn't match API routes"""
    # Skip API routes - let them be handled by the API routers
    if full_path == "api" or full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    from fastapi.responses import FileResponse, HTMLResponse
    import os
    
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'client', 'dist'))
    
    # First, try to serve the requested file (for static assets like CSS, JS, images)
    file_path = os.path.join(frontend_path, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # If file doesn't exist, serve index.html (for frontend routes like /login, /chat, etc.)
    index_path = os.path.join(frontend_path, 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3080,
        reload=True,
        log_level="info"
    )