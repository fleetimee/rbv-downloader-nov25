from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="RBV Downloader API")

# Register Routers
app.include_router(api_router, prefix="/api")
