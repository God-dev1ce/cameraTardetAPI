from typing import List
from pydantic import BaseModel

class DeviceModelMap(BaseModel):
    device_id: str
    model_id: List[str]  # 改为数组类型
    class Config:
        orm_mode = True