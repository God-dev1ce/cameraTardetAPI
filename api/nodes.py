import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Node, Device
from schemas.node import NodeBase, NodeCreate
from typing import List, Dict, Any, Optional
from core.security import get_password_hash, decodeToken2user
from utils.response import success_response, error_response

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
#创建节点
@router.post("/api/addNode")
def create_node(node_in: NodeCreate, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID,current_userRole= current_userInfo  
    if current_userRole != "admin":
        return error_response(code=400, msg="无权限")
    
    parent_node = db.query(Node).filter(Node.id == node_in.parent_id).first()
    if not parent_node:
        return error_response(code=400, msg="父节点不存在")
    new_node_js = int(parent_node.node_js) + 1
    parent_fjm = parent_node.node_fjm
    last_node = db.query(Node).filter(Node.node_js == new_node_js, Node.node_fjm.like(parent_fjm + "%")).order_by(Node.node_fjm.desc()).first()
    if not last_node:
        new_node_fjm = parent_fjm + "001"  
    if last_node:
        new_node_fjm = last_node.node_fjm[:-3] + str(int(last_node.node_fjm[-3:]) + 1).zfill(3)
        
    existing_node = db.query(Node).filter(Node.node_fjm == new_node_fjm).first()
    if existing_node:   
        return error_response(code=400, msg="节点分级码重复")

    # 创建新节点
    new_node = Node(
        id=uuid.uuid4(),
        name=node_in.node_name,
        parent_id=node_in.parent_id,
        node_js=new_node_js,
        node_fjm=new_node_fjm,
        node_mx="1"
    )
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    parent_node.node_mx = "0"
    db.commit()
    db.refresh(parent_node)
    
    return success_response(msg="节点创建成功")

#获取节点列表
@router.get("/api/getNodesList")
def list_nodes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),checkToken = Depends(decodeToken2user)):
    if checkToken==False:
        return error_response(code=401, msg="令牌验证失败")
    total = db.query(Node).count()
    nodes = db.query(Node).order_by(Node.node_fjm.asc()).offset(skip).limit(limit).all()
    # nodes_out = jsonable_encoder(nodes)
    nodes_out = [{"id": str(node.id), "name": node.name, "parent_id": node.parent_id, 
                  "node_js": node.node_js, "node_fjm": node.node_fjm, "node_mx": node.node_mx} for node in nodes]
    return success_response(data={"total": total, "nodes": nodes_out}, msg="获取节点列表成功")

# 获取节点树状结构
@router.get("/api/getNodesTree")
def get_nodes_tree(db: Session = Depends(get_db), checkToken=Depends(decodeToken2user)):
    if checkToken == False:
        return error_response(code=401, msg="令牌验证失败")
    
    nodes = db.query(Node).order_by(Node.node_fjm.asc()).all()
    
    nodes_dict = []
    for node in nodes:
        nodes_dict.append({
            "id": node.id,
            "name": node.name,
            "parent_id": node.parent_id,
            "node_js": node.node_js,
            "node_fjm": node.node_fjm,
            "node_mx": node.node_mx,
            "children": []
        })
    
    # 构建树状结构
    tree = []
    node_map = {node["node_fjm"]: node for node in nodes_dict}
    
    for node in nodes_dict:
        if len(node["node_fjm"]) == 3:
            tree.append(node)
        else:
            parent_fjm = node["node_fjm"][:-3]
            if parent_fjm in node_map:
                node_map[parent_fjm]["children"].append(node)
    
    return success_response(data=tree, msg="获取节点树状结构成功")

#删除节点
@router.delete("/api/deleteNode/{node_id}") 
def delete_node(node_id: str, db: Session = Depends(get_db),current_userInfo = Depends(decodeToken2user)):
    if current_userInfo==False:
        return error_response(code=401, msg="令牌验证失败")
    current_userID,current_userRole= current_userInfo  
    if current_userRole!= "admin":
        return error_response(code=400, msg="无权限")
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        return error_response(code=400, msg="节点不存在")
    child_nodes = db.query(Node).filter(Node.node_fjm.like(node.node_fjm + "%")).all()
    for child_node in child_nodes:
        db.delete(child_node)
    db.delete(node)
    db.commit()
    return success_response(msg="节点删除成功")
