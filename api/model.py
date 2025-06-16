from datetime import datetime
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal    
from db.models import Model,Model_Rule,Device_Model_Map,Device_Model_Rule_Map,Alerts_Type
from schemas.model import ModelCreate, ModelUpdate
from schemas.device_model_rule_map import DeviceModelRuleMap
from core.security import decodeToken2user
from fastapi.encoders import jsonable_encoder
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
    #检查报警类型ID
    alert_type = db.query(Alerts_Type).filter(Alerts_Type.id == model.alert_type).first()
    if not alert_type:
        return error_response(code=400, msg="报警类型不存在")
    # 创建新模型
    new_model = Model(
        id=uuid.uuid4(),
        name=model.name,
        alert_type=model.alert_type,
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
    if model_in.alert_type:
        #检查报警类型ID
        alert_type = db.query(Alerts_Type).filter(Alerts_Type.id == model_in.alert_type).first()
        if not alert_type:
            return error_response(code=400, msg="报警类型不存在")
    for key, value in model_in.model_dump(exclude_unset=True).items():
        setattr(model, key, value)
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

#获取模型列表
@router.get("/api/getModelList")
def get_model_list(db: Session = Depends(get_db), current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID, current_userRole = current_userInfo
    if current_userRole != "admin":
        return error_response(code=400, msg="无权限")
    models = db.query(Model).all()
    if not models:
        return error_response(code=404, msg="模型不存在")
    resData = []
    for model in models:
        resData.append({
            **jsonable_encoder(model),
        })
    total = len(resData)
    resData = {
        "total": str(total),
        "models": resData
    }
    return success_response(data=resData,msg="查询模型列表成功")


#模型绑定识别规则
@router.post("/api/bindRuleToModel")
def bind_model_rule(map_in:DeviceModelRuleMap, db: Session = Depends(get_db), current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID, current_userRole = current_userInfo
    if current_userRole != "admin":
        return error_response(code=400, msg="无权限")
    
    model = db.query(Device_Model_Map).filter(Device_Model_Map.id == map_in.device_model_id).first()
    if not model:
        return error_response(code=404, msg="该设备和模型绑定关系不存在")
    new_map = None
    
    for rule_id in map_in.rule_id:  
        model_rule = db.query(Model_Rule).filter(Model_Rule.id == rule_id).first()
        if not model_rule:
            return error_response(code=404, msg=f"规则 {rule_id} 不存在")
        
        existing_rule = db.query(Device_Model_Rule_Map).filter(
            Device_Model_Rule_Map.device_model_id == map_in.device_model_id,
            Device_Model_Rule_Map.rule_id == rule_id
        ).first()
        if existing_rule:
            continue
        
        new_map = Device_Model_Rule_Map(
            id=uuid.uuid4(),
            device_model_id=map_in.device_model_id,
            rule_id=rule_id
        )
        db.add(new_map)
    
    if not new_map:
        return error_response(code=400, msg="都已绑定，没有新的识别规则绑定")
    db.commit()
    db.refresh(new_map)
    return success_response(msg="识别规则绑定成功")