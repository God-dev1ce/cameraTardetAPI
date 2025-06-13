# 路由逻辑
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import User
from schemas.auth import LoginRequest, RefreshTokenRequest
from core.security import verify_password, create_access_token,create_refresh_token
from utils.response import success_response, error_response
from datetime import timedelta
from jose import JWTError, jwt
from utils.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#登录接口
@router.post("/api/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.usercode == request.usercode).first()
    if not user or not verify_password(request.password, user.password):
        return error_response(code=400, msg="用户名或密码错误")
    # 生成 access_token 和 refresh_token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
    )
    resData = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
    return success_response(data=resData, msg="登录成功")


# 刷新令牌接口 access_token失效会返回401 Unauthorized错误，此时可以使用refresh_token来获取新的access_token
@router.post("/api/refresh")
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        # 从请求体中获取 refresh_token
        refresh_token = request.refresh_token

        # 解码 refresh_token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return error_response(code=401, msg="无效的令牌")
        
        # 查询用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return error_response(code=404, msg="用户不存在")

        # 生成新的 access_token
        new_access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
        )
        resData = {"access_token": new_access_token, "token_type": "bearer"}
        return success_response(data=resData, msg="刷新令牌成功")
    except JWTError:
        return error_response(code=401, msg="令牌验证失败")

