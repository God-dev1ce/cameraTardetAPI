from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceBase(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[str] = None
    director: Optional[str] = None
    node_id: Optional[str] = None
    connected_time: Optional[datetime] = None
    disconnected_time: Optional[datetime] = None
    is_online: Optional[int] = 0
    sync_time: Optional[datetime] = None
    
class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    pass
