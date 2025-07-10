import requests
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import osmnx as ox
import networkx as nx
from backend.api import predict
from fastapi import APIRouter
from backend.database.schema import RouteRequest, RouteResponse, RouteLog
import polyline  # pip install polyline

router = APIRouter()

class PredictRequest(BaseModel):
    start: List[float]  # [lat, lon]
    end: List[float]    # [lat, lon]
    disabled_type: str

    # OpenRouteService API 키
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjY2ZjQ5MmIyNjVhZDQ3MmZhNGY4YTYxNzlhZjFjNGUzIiwiaCI6Im11cm11cjY0In0="


@router.post("/predict")
def predict_route(req: PredictRequest):
    try:
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        }

        url = "https://api.openrouteservice.org/v2/directions/foot-walking"

        payload = {
            "coordinates": [
                req.start[::-1],  # [lon, lat]
                req.end[::-1]
            ]
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        route_data = response.json()
        print("✅ 받은 응답:", route_data)

        if "routes" not in route_data:
            return {
                "error": "경로 요청 중 오류 발생",
                "details": str(route_data)
            }

        # ✅ geometry를 디코딩해서 lat/lng 배열로 변환
        encoded_polyline = route_data["routes"][0]["geometry"]
        decoded_coords = polyline.decode(encoded_polyline)  # [(lat, lon), (lat, lon), ...]

        return {
            "route": decoded_coords  # leaflet에 바로 넘길 수 있음
        }

    except Exception as e:
        print("❌ 경로 요청 실패:", e)
        return {
            "error": "경로 요청 중 오류 발생",
            "details": str(e)
        }