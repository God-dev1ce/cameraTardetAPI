from datetime import datetime
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal    
from db.models import Model_Rule,Model
from schemas.model_rule import RuleCreate, RuleUpdate
from core.security import decodeToken2user
from utils.response import success_response, error_response

router = APIRouter()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# 新增识别规则
@router.post("/api/addModelRule")
def create_model(rule_in: RuleCreate, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID,current_userRole= current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")
    model_rule = db.query(Model_Rule).filter(Model_Rule.name == rule_in.name).first()
    if model_rule:
        return error_response(code=400, msg="识别规则名称重复")
    model = db.query(Model).filter(Model.id == rule_in.model_id).first()
    if not model:
        return error_response(code=404, msg="所属模型不存在")
    # 创建新识别规则
    new_rule = Model_Rule(
        id=uuid.uuid4(),
        name=rule_in.name,
        model_id=rule_in.model_id,
        path=rule_in.path,
        notes=rule_in.notes
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return success_response(msg="新增识别规则成功")

# 更新识别规则
@router.post("/api/updateModelRule")
def update_model(rule_in: RuleUpdate, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID,current_userRole= current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")
    model_rule = db.query(Model_Rule).filter(Model_Rule.id == rule_in.id).first()
    if model_rule:
        return error_response(code=404, msg="识别规则不存在")
    for key, value in rule_in.model_dump(exclude_unset=True,exclude=['id','path']).items():
        setattr(model_rule, key, value)
    db.commit()
    db.refresh(model_rule)
    return success_response(msg="更新识别规则成功")

# 删除识别规则
@router.delete("/api/deleteModelRule/{rule_id}")
def delete_model_rule(rule_id: str, db: Session = Depends(get_db), current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID,current_userRole= current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")
    
    model_rule = db.query(Model_Rule).filter(Model_Rule.id == rule_id).first()
    if not model_rule:
        return error_response(code=404, msg="识别规则不存在")
    
    db.delete(model_rule)
    db.commit()
    return success_response(msg="删除识别规则成功")