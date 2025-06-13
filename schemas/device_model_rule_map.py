from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceModelRuleMap(BaseModel):
    id: Optional[str] = None
    device_model_id: Optional[str] = None
    rule_id: Optional[str] = None