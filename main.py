from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, device_play, nodes, users, devices,model,model_rule,alerts,alerts_type
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("🚀 FastAPI 应用正在启动！")

app = FastAPI()
# 允许前端地址跨域访问你的后端API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # 如果你用其他端口或者域名，也可以加上
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,      
    allow_methods=["*"],         
    allow_headers=["*"],         
)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(devices.router)
app.include_router(nodes.router)
app.include_router(model.router)
app.include_router(model_rule.router)
app.include_router(device_play.router)
app.include_router(alerts.router)
app.include_router(alerts_type.router)

