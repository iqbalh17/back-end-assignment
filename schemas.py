from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MenuCreate(BaseModel):
    name: str
    category: str
    price: float
    calories: Optional[int] = 0
    ingredients: List[str] = []
    description: Optional[str] = None

class MenuResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    calories: int
    ingredients: List[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    data: List[MenuResponse]
    pagination: dict

class HealthCheckResponse(BaseModel):
    menu_name: str
    allergens: List[str]  
    diet_labels: List[str] 
    health_score: int     
    advice: str

class BurnActivity(BaseModel):
    activity: str  
    duration: str  
    intensity: str  

class BurnCaloriesResponse(BaseModel):
    menu_name: str
    calories: int
    exercises: List[BurnActivity]           

