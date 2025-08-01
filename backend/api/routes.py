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
from sqlalchemy import text
from sqlalchemy import create_engine
from backend.database.db import engine
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from fastapi import Query

router = APIRouter()

class PredictRequest(BaseModel):
    start: List[float]  # [lat, lon]
    end: List[float]    # [lat, lon]
    disabled_type: str

    # OpenRouteService API 키
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjY2ZjQ5MmIyNjVhZDQ3MmZhNGY4YTYxNzlhZjFjNGUzIiwiaCI6Im11cm11cjY0In0="

@router.get("/facilities/{user_type}")
async def get_facilities(
    user_type: str,
    minLat: float = Query(None),
    minLon: float = Query(None),
    maxLat: float = Query(None),
    maxLon: float = Query(None)
):
    if user_type not in ["wheelchair", "stroller", "elderly", "night"]:
        raise HTTPException(status_code=400, detail="Invalid user type")

    # stroller은 wheelchair과 동일 처리
    if user_type == "stroller":
        weight_column = "weight_wheelchair"
    else:
        weight_column = f"weight_{user_type}"

    # 기본 쿼리 구성
    base_query = f"""
        SELECT id, facility_id, latitude, longitude, {weight_column} AS weight
        FROM facilities
        WHERE {weight_column} > 0
    """

    # 범위 필터링이 들어오면 조건 추가
    conditions = []
    params = {}

    if all(v is not None for v in [minLat, maxLat, minLon, maxLon]):
        conditions.append("latitude BETWEEN :minLat AND :maxLat")
        conditions.append("longitude BETWEEN :minLon AND :maxLon")
        params.update({
            "minLat": minLat,
            "maxLat": maxLat,
            "minLon": minLon,
            "maxLon": maxLon
        })

    if conditions:
        base_query += " AND " + " AND ".join(conditions)

    query = text(base_query)

    with engine.connect() as conn:
        result = conn.execute(query, params)
        rows = result.fetchall()

    features = []
    for row in rows:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row.longitude, row.latitude]
            },
            "properties": {
                "id": row.id,
                "facility_id": row.facility_id,
                "weight": row.weight
            }
        }
        features.append(feature)

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return JSONResponse(content=geojson)


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