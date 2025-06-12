#用户信息相关Pydantic 模型
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class RoleEnum(str, Enum):
    admin = "admin"
    user = "user"

class UserBase(BaseModel):
    usercode: str
    username: str
    role: RoleEnum
    creator_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    usercode: str
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None

class UserOut(UserBase):
    id: int
    created_time: Optional[datetime] = None

    model_config = {"from_attributes": True}

class UserListResponse(BaseModel):
    total: int
    users: list[UserOut]
    model_config = {
        "from_attributes": True  
    }
