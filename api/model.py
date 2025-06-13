from datetime import datetime
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal    
from db.models import Model
from schemas.model import ModelCreate, ModelUpdate
from core.security import decodeToken2user
from utils.response import success_response, error_response

router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# 新增模型
@router.post("/api/addModel")
def create_model(model: ModelCreate, db: Session = Depends(get_db), current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID, current_userRole = current_userInfo
    if current_userRole != "admin":
        return error_response(code=400, msg="无权限")
    existing_model = db.query(Model).filter(Model.name == model.name).first()
    if existing_model:
        return error_response(code=400, msg="模型名称重复")
    
    # 创建新模型
    new_model = Model(
        id=uuid.uuid4(),
        name=model.name,
        created_time=datetime.now()
    )
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return success_response(msg="新增模型成功")

# 更新模型
@router.post("/api/updateModel")
def update_model(model_in: ModelUpdate, db: Session = Depends(get_db), current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID, current_userRole = current_userInfo
    if current_userRole != "admin":
        return error_response(code=400, msg="无权限")
    model = db.query(Model).filter(Model.id == model_in.id).first()
    if not model:
        return error_response(code=404, msg="模型不存在")
    model.name = model_in.name
    db.commit()
    db.refresh(model)
    return success_response(msg="更新模型成功")

# 删除模型
@router.delete("/api/deleteModel/{model_id}")
def delete_model(model_id: str, db: Session = Depends(get_db), current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID, current_userRole = current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        return error_response(code=404, msg="模型不存在")
    db.delete(model)
    db.commit() 
    return success_response(msg="删除模型成功")