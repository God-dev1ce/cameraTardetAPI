from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ModelBase(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    alert_type: Optional[str] = None
    created_time: Optional[datetime] = None
class ModelCreate(ModelBase):
    name: str
    alert_type:str

class ModelUpdate(ModelBase):
    id: str
