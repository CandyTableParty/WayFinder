from pydantic import BaseModel
from typing import List
from pydantic import BaseModel
from typing import List, Literal

class RouteRequest(BaseModel):
    start: List[float]       # [lat, lon]
    end: List[float]         # [lat, lon]
    disabled_type: Literal["wheelchair", "stroller", "elderly"]

class RouteResponse(BaseModel):
    route: List[List[float]]  # [[lat1, lon1], [lat2, lon2], ...]

    
class RouteLog(BaseModel):
    user_id: str
    start: List[float]
    end: List[float]
    disabled_type: str
    route: List[List[float]]
    avoided_points: List[List[float]]
    time_taken: int
