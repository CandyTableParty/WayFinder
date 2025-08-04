from fastapi import APIRouter
from pydantic import BaseModel
from backend.models.knn_model import knn_recommend_route

router = APIRouter()

class RouteRequest(BaseModel):
    start: list  # [lat, lon]
    end: list
    disabled_type: str

@router.post("/predict-route")
async def predict_route(req: RouteRequest):
    route = knn_recommend_route(req.start, req.end, req.disabled_type)
    return {"recommended_route": route}
