from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RuleBase(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    model_id: Optional[str] = None
    path: Optional[str] = None
    notes: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
class RuleCreate(RuleBase):
    name: str
    model_id: str
    path: str
class RuleUpdate(RuleBase):
    id: str
