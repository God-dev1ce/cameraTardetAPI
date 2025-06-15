import uuid
import cv2
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Device, Node,Model,Device_Model_Map
from schemas.device import DeviceCreate, DeviceUpdate
from schemas.device_model_map import DeviceModelMap
from typing import List, Optional
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

    # 使用 model_dump() 替代 dict()
    for key, value in device_in.model_dump(exclude_unset=True).items():
        setattr(device, key, value)

    db.commit()
    db.refresh(device)
    return success_response(msg="设备信息更新成功")

#绑定模型
@router.post("/api/bindModelToDevice")
def bind_model_to_device(
    map_in : DeviceModelMap,
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
    models=map_in.model_id.split(",")
    for model_id in models:
        model = db.query(Model).filter(Model.id == model_id).first()
        if not model:
            return error_response(code=404, msg=f"模型 {model_id} 不存在")
        
        existing_map = db.query(Device_Model_Map).filter(
            Device_Model_Map.device_id == map_in.device_id,
            Device_Model_Map.model_id == model_id
        ).first()
        #如果已经绑定过，就跳过
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
