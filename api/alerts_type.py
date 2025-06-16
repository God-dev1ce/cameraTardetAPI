from datetime import datetime
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal    
from db.models import Alerts_Type
from schemas.alerts_type import AlertTypeCreate,AlertTypeUpdate
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

#新增报警类型
@router.post("/api/addAlertType")
def create_alert_type(alert_type: AlertTypeCreate, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID, current_userRole = current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")
    
    db_alert_type = Alerts_Type(name=alert_type.name)
    #自动计算idx
    max_idx = db.query(Alerts_Type.idx).order_by(Alerts_Type.idx.desc()).first()
    if max_idx:
        db_alert_type.idx = max_idx.idx + 1
    else:
        db_alert_type.idx = 1
    db_alert_type.id = str(uuid.uuid4())
    db.add(db_alert_type)
    db.commit()
    db.refresh(db_alert_type)
    return success_response(msg="新增报警类型成功")
#获取报警类型列表
@router.get("/api/getAlertTypesList")
def get_alert_types(db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")
    alert_types = db.query(Alerts_Type).order_by(Alerts_Type.idx).all()
    if not alert_types:
        return error_response(code=404, msg="报警类型列表为空")  
    resData = []
    for alert_type in alert_types:
        resData.append({
            **jsonable_encoder(alert_type),
        })
    return success_response(data=resData,msg="获取报警类型列表成功")

#更新报警类型
@router.post("/api/updateAlertType")
def update_alert_type(alert_type: AlertTypeUpdate, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID, current_userRole = current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")
    db_alert_type = db.query(Alerts_Type).filter(Alerts_Type.id == alert_type.id).first()
    if not db_alert_type:
        return error_response(code=404, msg="报警类型不存在")
    db_alert_type.name = alert_type.name
    db_alert_type.idx = alert_type.idx
    #判断是否有重复idx
    if db.query(Alerts_Type).filter(Alerts_Type.idx == alert_type.idx).first():
        return error_response(code=400, msg="报警类型idx序号重复")
    db.commit()
    return success_response(msg="更新报警类型成功")
#删除报警类型
@router.delete("/api/deleteAlertType/{alert_id}")
def delete_alert_type(alert_id: str, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID, current_userRole = current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")
    db_alert_type = db.query(Alerts_Type).filter(Alerts_Type.id == alert_id).first()
    if not db_alert_type:
        return error_response(code=404, msg="报警类型不存在")
    db.delete(db_alert_type)
    db.commit()
    return success_response(msg="删除报警类型成功")



