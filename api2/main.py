from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

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
from app.routes import auth, config, banner, endpoints, user, conversations, models, files, search, roles, agents, keys, presets, messages, memory
app.include_router(auth.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(banner.router, prefix="/api")
app.include_router(endpoints.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(conversations.router, prefix="/api/convos")
app.include_router(models.router, prefix="/api")
app.include_router(files.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(roles.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(keys.router, prefix="/api")
app.include_router(presets.router, prefix="/api")
app.include_router(messages.router, prefix="/api/convos")
app.include_router(memory.router, prefix="/api/memory")

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
        port=8000,
        reload=True,
        log_level="info"
    )