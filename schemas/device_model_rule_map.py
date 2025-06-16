from typing import List
from pydantic import BaseModel

class DeviceModelRuleMap(BaseModel):
    device_model_id: str
    rule_id: List[str]  # 改为数组类型
    class Config:
        orm_mode = True