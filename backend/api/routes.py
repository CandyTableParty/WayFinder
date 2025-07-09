from fastapi import APIRouter
from backend.api import predict

router = APIRouter()
router.include_router(predict.router, tags=["predict"])
