from pydantic import BaseModel
from typing import List

class Polygon(BaseModel):
    coordinates: List[List[float]]  # [[x,y], [x,y], ...]

class CreateWallRequest(BaseModel):
    name: str
    geometry: Polygon

class CreateObstacleRequest(BaseModel):
    type: str
    geometry: Polygon

class PlanRequest(BaseModel):
    resolution: float = 0.1

class WallResponse(BaseModel):
    wall_id: str

class PlanCandidate(BaseModel):
    path_id: str
    coverage: float
    path_length: int

class PlanResponse(BaseModel):
    plan_id: str
    best_path_id: str
    candidates: List[PlanCandidate]