import logging
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth
from app.api.endpoints import chat
from app.api.endpoints import kb
from app.api.endpoints import settings as user_settings

def _setup_logging() -> None:
    """Route app logs through uvicorn logger and set INFO level for our modules."""
    uvicorn_logger = logging.getLogger("uvicorn.error")
    targets = [
        "app.services.chat_service",
        "app.services.llm_service",
        "app.crud.crud_chat",
        "app.api.endpoints.chat",
    ]
    for name in targets:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        if uvicorn_logger.handlers:
            logger.handlers = uvicorn_logger.handlers
        logger.propagate = False


_setup_logging()

app = FastAPI(title="FastAPI Project Template")

# Main router with /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(kb.router, prefix="/kb", tags=["Knowledge Base"])
api_router.include_router(user_settings.router, prefix="/settings", tags=["Settings"])

app.include_router(api_router)

# CORS for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
