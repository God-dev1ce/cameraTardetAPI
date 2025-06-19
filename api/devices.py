import uuid
import cv2
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Device, Node,Model,Model_Rule,Device_Model_Map,Device_Model_Rule_Map
from schemas.device import DeviceCreate, DeviceUpdate
from schemas.device_model_map import DeviceModelMap
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from core.security import  decodeToken2user,aes_encrypt
from utils.response import success_response, error_response

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# 创建设备
@router.post("/api/addDevice")
def create_device(
    device_in: DeviceCreate, 
    db: Session = Depends(get_db), 
    current_userInfo = Depends(decodeToken2user)
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")
    
    current_userID, current_userRole = current_userInfo  
    if current_userRole != "admin":
        return error_response(code=400, msg="无权限")
    
    existing_device = db.query(Device).filter(Device.code == device_in.code).first()
    if existing_device:
        return error_response(code=400, msg="设备已存在")
    
    # 将device_in参数映射到Device模型
    device_data = device_in.model_dump(exclude_unset=True)
    new_device = Device(
        id=uuid.uuid4(),
        admin_pwd = aes_encrypt(device_data.pop('admin_pwd')),
        **device_data
    )
    
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    
    return success_response(msg="设备创建成功")

#删除设备
@router.delete("/api/deleteDevice/{device_id}")
def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_userInfo = Depends(decodeToken2user) 
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")

    current_userID, current_userRole = current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")

    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        return error_response(code=404, msg="设备不存在")

    db.delete(device)
    db.commit()

    return success_response(msg="设备删除成功")

#获取未绑定节点的设备列表
@router.get("/api/getUnbindedDeviceList")
def get_unbinded_device_list(
    db: Session = Depends(get_db),
    current_userInfo = Depends(decodeToken2user) 
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")

    current_userID, current_userRole = current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")
    #查询node_id为空的设备或者node_id=null的设备
    
    unbinded_devices = db.query(Device).filter(Device.node_id == None).all()
    if not unbinded_devices:
        return error_response(code=404, msg="未查询到未绑定节点的设备")  
    resData = []
    resData = [{
        **jsonable_encoder(device),
        "connected_time": device.connected_time.isoformat() if device.connected_time else None,
        "disconnected_time": device.disconnected_time.isoformat() if device.disconnected_time else None,
        "sync_time": device.sync_time.isoformat() if device.sync_time else None
    } for device in unbinded_devices]
    total = db.query(Device).filter(Device.node_id == None).count()
    resData = {
        "total": str(total),
        "devices": resData
    }
    return success_response(data=resData, msg="获取未绑定节点的设备列表成功")

#获取设备统计信息
@router.get("/api/getDevicesStats")
def get_devices_stats(
    db: Session = Depends(get_db),
    current_userInfo = Depends(decodeToken2user) 
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")

    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.is_online == "1").count()
    offline_devices = db.query(Device).filter(Device.is_online == "0").count()

    resData = {
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices
    }
    
    return success_response(data=resData, msg="获取设备统计信息成功")

#更新设备信息
@router.post("/api/updateDevice")
def update_device(
    device_in: DeviceUpdate,
    db: Session = Depends(get_db),
    current_userInfo = Depends(decodeToken2user) 
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")

    current_userID, current_userRole = current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")

    device = db.query(Device).filter(Device.id == device_in.id).first()
    if not device:
        return error_response(code=404, msg="设备不存在")

    for key, value in device_in.model_dump(exclude_unset=True,exclude=['id','ip_address','port','admin_account','admin_pwd']).items():
        setattr(device, key, value)

    db.commit()
    db.refresh(device)
    return success_response(msg="设备信息更新成功")

#绑定模型
@router.post("/api/bindModelToDevice")
def bind_model_to_device(
    map_in: DeviceModelMap,
    db: Session = Depends(get_db),
    current_userInfo = Depends(decodeToken2user) 
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")

    current_userID, current_userRole = current_userInfo
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")

    device = db.query(Device).filter(Device.id == map_in.device_id).first()
    if not device:
        return error_response(code=404, msg="设备不存在")
    
    new_map = None
    # 直接使用数组形式的model_id
    for model_id in map_in.model_id:
        model = db.query(Model).filter(Model.id == model_id).first()
        if not model:
            return error_response(code=404, msg=f"模型 {model_id} 不存在")
        
        existing_map = db.query(Device_Model_Map).filter(
            Device_Model_Map.device_id == map_in.device_id,
            Device_Model_Map.model_id == model_id
        ).first()
        if existing_map:
            continue
        
        new_map = Device_Model_Map(
            id=uuid.uuid4(),
            device_id=map_in.device_id,
            model_id=model_id
        )
        db.add(new_map)
    
    if not new_map:
        return error_response(code=400, msg="没有新的模型绑定")
    db.commit()
    db.refresh(new_map)
    return success_response(msg="模型绑定成功")

#获取设备下设置的模型和规则
@router.get("/api/getDeviceBindInfo/{device_id}")
def get_device_bind_info(
    device_id: str,
    db: Session = Depends(get_db),
    current_userInfo = Depends(decodeToken2user) 
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")

    # 查询设备绑定的所有模型
    device_models = db.query(Device_Model_Map).filter(Device_Model_Map.device_id == device_id).all()
    if not device_models:
        return error_response(code=404, msg="设备未绑定任何模型")
    resData = []
    
    for device_model in device_models:
        resData.append({
            "model_id": device_model.model_id,
            "model_name": db.query(Model).filter(Model.id == device_model.model_id).first().name,
            "rules": []
        })
        #查询该设备绑定的模型下绑定的所有规则
        device_model_rules = db.query(Device_Model_Rule_Map).filter(Device_Model_Rule_Map.device_model_id == device_model.id).all()
        for device_model_rule in device_model_rules:
            resData[-1]["rules"].append({
                "rule_id": device_model_rule.rule_id,
                "rule_name": db.query(Model_Rule).filter(Model_Rule.id == device_model_rule.rule_id).first().name,
            })
    #返回数据
    return success_response(data=resData, msg="获取设备绑定信息成功")
        
        
    

#获取设备24小时在线情况
@router.get("/api/getDeviceOnlineInfo")
def get_device_online_stats(
    current_userInfo = Depends(decodeToken2user) 
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")

    # 生成24小时的模拟数据
    import random
    from datetime import datetime, timedelta
    
    now = datetime.now()
    hours_data = []
    
    for i in range(24):
        hour = (now - timedelta(hours=23 - i)).strftime("%H:00")
        # 固定总设备数100，随机生成在线设备数(0-100)
        online_devices = random.randint(0, 100)
        hours_data.append({
            "time": hour,
            "total_devices": 100,
            "online_devices": online_devices
        })

    return success_response(data=hours_data, msg="获取设备历史在线信息成功")
