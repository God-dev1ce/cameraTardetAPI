import cv2
import base64
import asyncio
import subprocess
import platform
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect, WebSocketState
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Device, Device_Company
from core.security import aes_decrypt
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
    cap = None

    try:
        # 获取设备和厂商信息
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            await websocket.send_text("404|设备不存在")
            return
        device_company = db.query(Device_Company).filter(Device_Company.id == device.company_id).first()
        if not device_company:
            await websocket.send_text("404|设备厂商不存在")
            return

        complete_ip = f"{device.ip_address}:{device.port}"
        adminInfo = f"{device.admin_account}:{aes_decrypt(device.admin_pwd)}"
        rtsp_url = f"{device_company.stream_type}://{adminInfo}@{complete_ip}{device_company.stream_path}"

        # ping 设备连通性
        ping_cmd = ['ping', '-n', '1', device.ip_address] if platform.system() == 'Windows' else ['ping', '-c', '1', device.ip_address]
        result = subprocess.run(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
        if result.returncode != 0:
            await websocket.send_text("400|设备IP不可达")
            return

        # 打开视频流
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            await websocket.send_text("400|无法打开直播流")
            return

        while True:
            if websocket.application_state != WebSocketState.CONNECTED:
                break

            ret, frame = cap.read()
            if not ret:
                await asyncio.sleep(0.1)
                continue

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
            _, buffer = cv2.imencode(".jpg", frame, encode_param)
            img_base64 = base64.b64encode(buffer).decode("utf-8")
            message = f"data:image/jpeg;base64,{img_base64}"

            try:
                await websocket.send_text("200|" + message)
            except RuntimeError:
                # 客户端断开时发送失败
                break

            await asyncio.sleep(0.03)

    except WebSocketDisconnect:
        print(f"客户端断开: {websocket.client}")
    except asyncio.CancelledError:
        print("WebSocket任务被取消")
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if cap:
            cap.release()
        # 避免重复关闭报错
        if websocket.application_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close()
            except RuntimeError:
                pass
        print("连接关闭")
