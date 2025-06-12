from pydantic import BaseModel
from typing import Optional, Any

class ResponseModel(BaseModel):
    code: int
    msg: str
    data: Optional[Any] = None  # 可选字段，用于返回具体数据