from fastapi import FastAPI, APIRouter
from app.api.endpoints import auth

app = FastAPI(title="FastAPI Project Template")

# Main router with /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
