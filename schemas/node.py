from pydantic import BaseModel
from typing import Optional

class NodeBase(BaseModel):
    node_name: str
    parent_id: str
    node_js: str
    node_fjm: str
    node_mx: str
class NodeCreate(BaseModel):
    node_name: str
    parent_id: str

