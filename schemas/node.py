from pydantic import BaseModel
from typing import Optional

class NodeBase(BaseModel):
    id: Optional[str] = None
    node_name: Optional[str] = None
    parent_id: Optional[str] = None
    node_js: Optional[str] = None
    node_fjm: Optional[str] = None
    node_mx: Optional[str] = None
class NodeCreate(BaseModel):
    node_name: str
    parent_id: str
class NodeUpdate(BaseModel):
    id: str
