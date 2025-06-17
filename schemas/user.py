#用户信息相关Pydantic 模型
from pydantic import BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class UserBase(BaseModel):
    id: Optional[str] = None
    usercode: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    creator_id: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    id: str