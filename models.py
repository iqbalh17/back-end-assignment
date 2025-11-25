from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from datetime import datetime

class Menu(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    price: float
    calories: int = 0
    description: Optional[str] = None
    
    ingredients: List[str] = Field(default=[], sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)