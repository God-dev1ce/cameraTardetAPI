from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceModelMap(BaseModel):
    id: Optional[str] = None
    device_id: Optional[str] = None
    model_id: Optional[str] = None