"""
FastAPI application initialization and configuration.
Main entry point for the backend server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_NAME, APP_VERSION, ALLOWED_ORIGINS, DEBUG
from app.database import create_all_tables
# Import models to register them with Base.metadata before create_all_tables()
import app.models  # noqa: F401
from app.routes import projects, titles, documents

# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="API for managing legal documents and encumbrances",
    debug=DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    create_all_tables()
    print(f"✓ {APP_NAME} v{APP_VERSION} started")
    print(f"✓ Database tables initialized")
    print(f"✓ API docs available at: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    print(f"✓ {APP_NAME} shutting down")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
    }


# Include routers
app.include_router(projects.router)
app.include_router(titles.router)
app.include_router(documents.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }
