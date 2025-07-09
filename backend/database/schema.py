from pydantic import BaseModel
from typing import List

class RouteLog(BaseModel):
    user_id: str
    start: List[float]
    end: List[float]
    disabled_type: str
    route: List[List[float]]
    avoided_points: List[List[float]]
    time_taken: int
