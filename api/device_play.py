import cv2
import base64
import asyncio
import subprocess
import platform
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Device
from fastapi import Depends

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/api/play/{device_id}")
async def rtsp_stream(
    websocket: WebSocket,
    device_id: str,
    db: Session = Depends(get_db)
):
    await websocket.accept()
    
    try:
        # 从数据库获取设备信息
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            await websocket.send_text("404|设备不存在")
            await websocket.close()
            return

        complete_ip = f"{device.ip_address}:{device.port}"
        adminInfo = f"{device.admin_account}:{device.admin_pwd}"

        # 先进行ping检测
        try:
            # 根据系统类型选择不同的ping参数
            ping_cmd = ['ping', '-n', '1', device.ip_address] if platform.system() == 'Windows' else ['ping', '-c', '1', device.ip_address]
            result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
            if result.returncode != 0:
                await websocket.send_text("400|设备IP不可达")
                await websocket.close()
                return
        except subprocess.TimeoutExpired:
            await websocket.send_text("400|ping检测超时")
            await websocket.close()
            return
        try:    
            rtsp_url = f"rts://{adminInfo}@{complete_ip}/Streaming/Channels/101"
            cap = cv2.VideoCapture(rtsp_url)
            
            if not cap.isOpened():
                await websocket.send_text("400|无法打开直播流")
                await websocket.close()
                return
        except Exception as e:
            await websocket.send_text("400|无效的直播流")
            await websocket.close()
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                continue
                
            _, buffer = cv2.imencode(".jpg", frame)
            img_base64 = base64.b64encode(buffer).decode("utf-8")
            message = f"data:image/jpeg;base64,{img_base64}"
            await websocket.send_text("200|"+message)
            
            await asyncio.sleep(0.03)
            
    except WebSocketDisconnect:
        print(f"客户端断开: {websocket.client}")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'cap' in locals():
            cap.release()
        await websocket.close()