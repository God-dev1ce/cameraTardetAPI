# SQLAlchemy模型定义
from sqlalchemy import Boolean, Column, Integer, String, Enum, DateTime, ForeignKey
from db.database import Base
import enum
from datetime import datetime

class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"
#用户表模型
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True) #用户ID
    usercode = Column(String(50),  nullable=False)  #用户编码
    username = Column(String(50),  nullable=False)  #用户名
    password = Column(String(100), nullable=False)  #密码
    role = Column(Enum(RoleEnum), nullable=False)   #用户角色
    creator_id = Column(String(36), nullable=True)  #创建者ID
    created_time = Column(DateTime, default=datetime.utcnow)    #创建时间
    
#设备表模型
class Device(Base):
    __tablename__ = "devices"

    id = Column(String(36), primary_key=True, index=True) #设备ID
    name = Column(String(20), nullable=False)  #摄像头名称
    code = Column(String(36), unique=True, nullable=False) #摄像头编码
    director = Column(String(30), nullable=True)   #设备负责人信息
    ip_address = Column(String(45), nullable=True)  #设备IP地址
    port = Column(String(10),  nullable=True)   #设备端口
    node_id = Column(String(36),  nullable=True)    #设备所在节点ID
    connected_time = Column(DateTime, nullable=True)    #设备连接时间
    disconnected_time = Column(DateTime, nullable=True)  #设备断开时间
    sync_time = Column(DateTime, nullable=True)  #设备同步时间
    is_online = Column(Boolean, default=False)   #设备在线状态
    
#节点表模型
class Node(Base):
    __tablename__ = "nodes"

    id = Column(String(36), primary_key=True, index=True)  #节点ID    
    name = Column(String(100), nullable=False)  #节点名称
    parent_id = Column(String(36), nullable=False)  #父节点ID
    node_js = Column(String(3), nullable=False) #节点级数
    node_fjm = Column(String(30), nullable=False)   #分级码
    node_mx = Column(String(1), nullable=False) #是否明细
    created_time = Column(DateTime, default=datetime.utcnow)    #创建时间

#报警表模型
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, index=True)   #报警ID
    device_id = Column(String(36),  nullable=False) #设备ID
    model_id = Column(String(36),  nullable=False)  #模型ID
    rule_id = Column(String(36),  nullable=False)   #识别规则ID
    image_url = Column(String(255), nullable=True)  #报警图片URL
    alert_msg = Column(String(255), nullable=True)  #报警信息
    alert_time = Column(DateTime, default=datetime.utcnow)    #报警时间
    alert_level = Column(Enum("A", "B", "C", "D"), nullable=True)   #报警级别
    alert_result = Column(Enum("误报", "确认报警"), nullable=True)  #报警结果
    status = Column(Enum("未确认", "已确认"), default="unhandled")  #处理状态
    handled_user = Column(String(36),  nullable=True)   #处理用户ID
    handled_time = Column(DateTime, nullable=True)   #处理时间

#模型表模型
class Model(Base):
    __tablename__ = "models"

    id = Column(String(36), primary_key=True, index=True)   #模型ID
    name = Column(String(20), nullable=False)   #模型名称
    created_time = Column(DateTime, default=datetime.utcnow)    #创建时间
    
# 模型规则表（权重）
class Model_Rule(Base):
    __tablename__ = "model_rules"

    id = Column(String(36), primary_key=True, index=True)   #模型规则ID
    name = Column(String(20), nullable=False)   #规则名称
    path = Column(String(255),  nullable=False) #规则文件路径
    nodes = Column(String(100),  nullable=False)    #适用节点列表
    created_time = Column(DateTime, default=datetime.utcnow)    #创建时间
    
# 关联模型规则表（权重）
class Device_Model_Map(Base):
    __tablename__ = "device_model_map"

    id = Column(String(36), primary_key=True, index=True)   #ID
    device_id = Column(String(36), nullable=False)   #设备ID
    model_id = Column(String(36),  nullable=False) #模型ID
    rules_id = Column(String(255),  nullable=False)    #绑定的规则ID列表

