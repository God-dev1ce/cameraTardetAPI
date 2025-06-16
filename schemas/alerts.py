from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class AlertBase(BaseModel):
    id: Optional[str] = None
    device_id: Optional[str] = None
    model_id: Optional[str] = None
    rule_id: Optional[str] = None
    image_url: Optional[str] = None
    alert_type: Optional[str] = None
    alert_msg: Optional[str] = None
    alert_time: Optional[datetime] = None
    alert_level: Optional[str] = None
    alert_result: Optional[str] = None
    status:Optional[str] = None
    handled_user: Optional[str] = None
    handled_time: Optional[datetime] = None
    class Config:
        orm_mode = True

class AlertCreate(AlertBase):
    device_id:str
    model_id:str
    rule_id:str
    image_url:str
    alert_type:str
    alert_msg:str
    class Config:
        orm_mode = True

class AlertUpdate(BaseModel):
    id: Union[str, List[str]]  # 支持字符串或字符串列表
    alert_result:str
    alert_level:str
    handled_user:str
    class Config:
        orm_mode = True

class AlertList(BaseModel):
    alert_type:Optional[str] = None
    device_id:Optional[str] = None
    start_time:Optional[datetime] = None
    end_time:Optional[datetime] = None
    status:Optional[str] = None
    class Config:
        orm_mode = True
