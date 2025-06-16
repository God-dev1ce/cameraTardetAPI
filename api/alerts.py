from datetime import datetime
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal    
from db.models import Model_Rule,Model,Alert,Device,Alerts_Type
from schemas.alerts import AlertCreate,AlertUpdate,AlertList
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
        
#新增报警记录
@router.post("/api/addAlert")
def add_alert(alert_in:AlertCreate, db: Session = Depends(get_db)):

    device = db.query(Device).filter(Device.id == alert_in.device_id).first()
    if not device:
        return error_response(code=400, msg="设备不存在")
    model = db.query(Model).filter(Model.id == alert_in.model_id).first()
    if not model:
        return error_response(code=400, msg="模型不存在")
    rule = db.query(Model_Rule).filter(Model_Rule.id == alert_in.rule_id).first()
    if not rule:
        return error_response(code=400, msg="规则不存在")
    alert_type = db.query(Alerts_Type).filter(Alerts_Type.id == alert_in.alert_type).first()
    if not alert_type:
        return error_response(code=400, msg="报警类型不存在")
    new_alert = Alert(
        id=str(uuid.uuid4()),
        device_id=alert_in.device_id,
        model_id=alert_in.model_id,
        rule_id=alert_in.rule_id,
        image_url=alert_in.image_url,
        alert_type=alert_in.alert_type,
        alert_msg=alert_in.alert_msg
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return success_response(msg="新增报警记录成功")

#处理报警记录
@router.post("/api/handleAlert")
def handle_alert(alert_in: AlertUpdate, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")
    # 支持单个ID或ID列表
    alert_ids = [alert_in.id] if isinstance(alert_in.id, str) else alert_in.id
    
    # 查询所有需要处理的报警记录
    alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
    if not alerts:
        return error_response(code=400, msg="未找到指定的报警记录")
    
    # 更新所有报警记录
    for alert in alerts:
        for key, value in alert_in.model_dump(exclude_unset=True, exclude=['id']).items():
            setattr(alert, key, value)
        alert.status="已处理"
        alert.handled_time = datetime.now()  # 设置处理时间为当前时间
    
    db.commit()
    return success_response(msg=f"成功处理{len(alerts)}条报警记录")

#查询报警记录列表
@router.get("/api/getAlertList")
def get_alert_list(
    alert_in: AlertList = Depends(),  # 使用Depends()使参数可选
    db: Session = Depends(get_db),
    current_userInfo = Depends(decodeToken2user)
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")
    
    # 构建基础查询
    query = db.query(Alert)
    
    # 如果有传入参数才添加过滤条件
    if any(value is not None for value in alert_in.dict().values()):
        filters = {
            'device_id': Alert.device_id,
            'model_id': Alert.model_id,
            'rule_id': Alert.rule_id,
            'alert_type': Alert.alert_type,
            'status': Alert.status
        }
        
        for field, column in filters.items():
            value = getattr(alert_in, field, None)
            if value is not None:
                query = query.filter(column == value)
        
        # 时间范围查询
        if alert_in.start_time:
            query = query.filter(Alert.alert_time >= alert_in.start_time)
        if alert_in.end_time:
            query = query.filter(Alert.alert_time <= alert_in.end_time)
    
    # 排序和获取结果
    alerts = query.order_by(Alert.alert_time.desc()).all()
    
    if not alerts:
        return error_response(code=404, msg="未找到符合条件的报警记录")
    
    resData = []
    for alert in alerts:
        resData.append({
            **jsonable_encoder(alert),
        })
    
    total = query.count()
    return success_response(
        data={
            "total": total,
            "alerts": resData
        },
        msg="查询报警记录成功"
    )


