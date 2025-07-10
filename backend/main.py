from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from backend.api.routes import router as api_router

app = FastAPI(title="Transport AI Navi")

# include API routes
app.include_router(api_router, prefix="/api")

# ✅ static 폴더 경로를 frontend로 지정
app.mount("/", StaticFiles(directory="frontend/static", html=True), name="static")

@app.get("/")
async def root():
    return {"status": "Transport AI Navi backend running"}