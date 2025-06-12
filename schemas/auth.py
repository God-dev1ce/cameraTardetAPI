# 登录认证相关Pydantic 模型
from pydantic import BaseModel

class LoginRequest(BaseModel):
    usercode: str
    password: str
class RefreshTokenRequest(BaseModel):
    refresh_token: str
