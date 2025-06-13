import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Device, Node
from schemas.device import DeviceCreate, DeviceUpdate
from typing import List, Optional
from core.security import get_password_hash, decodeToken2user
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
    
    new_device = Device(
        id=uuid.uuid4(),
        code=device_in.code,
        name=device_in.name,
        ip_address=device_in.ip_address,
        port=device_in.port
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


#获取节点下的设备列表
@router.get("/api/getDevicesByNode/{node_id}")
def list_devices_by_node(
    node_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_userInfo = Depends(decodeToken2user) 
):
    if current_userInfo == False:
        return error_response(code=401, msg="令牌验证失败")
    
    #根据node_id获取Node表所有的子节点id，包括自己
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        return error_response(code=404, msg="节点不存在")
    node_ids = [node.id]
    child_nodes = db.query(Node).filter(Node.node_fjm.like(node.node_fjm + "%")).all()
    for child_node in child_nodes:
        node_ids.append(child_node.id)
    devices = db.query(Device).filter(Device.node_id.in_(node_ids)).offset(skip).limit(limit).all( )
    if not devices:
        return error_response(code=404, msg="设备列表为空")  
    resData = []
    for device in devices:
        resData.append({
            "id": str(device.id),
            "name": device.name,
            "code": device.code,
            "director": device.director,
            "ip_address": device.ip_address,
            "port": device.port,
            "node_id": device.node_id,
            "connected_time": device.connected_time,
            "disconnected_time": device.disconnected_time,
            "sync_time": device.sync_time,
            "is_online": device.is_online
        })
    total = db.query(Device).filter(Device.node_id.in_(node_ids)).count()
    resData = {
        "total": total,
        "devices": resData
    }
    return success_response(data=resData, msg="获取设备列表成功")


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

    for key, value in device_in.dict(exclude_unset=True).items():
        setattr(device, key, value)

    db.commit()
    db.refresh(device)
    return success_response(msg="设备信息更新成功")

