from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class AlertType(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    idx: Optional[int] = None
    class Config:
        orm_mode = True
        
class AlertTypeCreate(BaseModel):
    name: str

class AlertTypeUpdate(BaseModel):
    id: str
