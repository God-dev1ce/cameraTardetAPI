# 用户接口逻辑
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.security import get_password_hash, decodeToken2user
from db.database import SessionLocal
from db.models import User
from schemas.user import UserCreate, UserUpdate
from utils.response import success_response, error_response
from fastapi.encoders import jsonable_encoder
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 获取用户列表（分页）
@router.get("/api/getUsers")
def list_users(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    checkToken=Depends(decodeToken2user)
):
    if checkToken==False:
        return error_response(code=401, msg="令牌验证失败")
    total = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    # users_out = jsonable_encoder(users)
    users_out = [{"usercode": user.usercode, "username": user.username,"role":user.role} for user in users]
    return success_response(data={"total": total, "users": users_out}, msg="获取用户列表成功")

# 新建用户
@router.post("/api/addUser")
def create_user(
    user_in: UserCreate, 
    db: Session = Depends(get_db), 
    current_userInfo = Depends(decodeToken2user)  
):
    
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID,current_userRole= current_userInfo 
    if current_userRole != "admin":
        return error_response(code=400, msg="无权限")

    existing_user = db.query(User).filter(User.usercode == user_in.usercode).first()
    if existing_user:
        return error_response(code=400, msg="用户已存在")
    
    # 创建新用户
    new_user = User(
        id=uuid.uuid4(),
        usercode=user_in.usercode,
        username=user_in.username,
        password=get_password_hash(user_in.password),
        role=user_in.role,
        creator_id=current_userID  
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return success_response(msg="用户创建成功")

# 获取单个用户详情
@router.get("/api/getUser/{usercode}")
def get_user(usercode: str, db: Session = Depends(get_db), checkToken=Depends(decodeToken2user)):
    if checkToken==False:
        return error_response(code=401, msg="令牌验证失败")
    user = db.query(User).filter(User.usercode == usercode).first()
    if not user:
        return error_response(code=404, msg="用户不存在")
    user_out = {
        "usercode": user.usercode,
        "username": user.username,
        "role": user.role
    }
    return success_response(data=user_out, msg="获取用户详情成功")

# 更新用户信息
@router.post("/api/updateUsers")
def update_user(user_in: UserUpdate, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID,current_userRole= current_userInfo  
    if current_userRole != "admin":
        return error_response(code=400, msg="无权限")
    user = db.query(User).filter(User.usercode == user_in.usercode).first()
    if not user:
        return error_response(code=400, msg="用户不存在")

    if user_in.username:
        user.username = user_in.username
    if user_in.password:
        user.password = get_password_hash(user_in.password)
    if user_in.role:
        user.role = user_in.role

    db.commit()
    db.refresh(user)
    # user_out = jsonable_encoder(user)
    user_out = {
        "usercode": user.usercode,
        "username": user.username,
        "role": user.role
    }
    return success_response(data=user_out, msg="用户更新成功")

# 删除用户
@router.delete("/api/delUsers/{usercode}")
def delete_user(usercode: str, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID,current_userRole= current_userInfo  
    if current_userRole != "admin":
        return error_response(code=400, msg="无权限删除用户")
    user = db.query(User).filter(User.usercode == usercode).first()
    if not user:
        return error_response(code=400, msg="用户不存在")

    db.delete(user)
    db.commit()
    return success_response(msg="用户删除成功")
