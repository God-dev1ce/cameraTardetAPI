# JWT相关逻辑  密码与JWT逻辑
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.models import User
from utils.response import success_response, error_response
from utils.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_DAYS
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

# AES加密密钥（开发阶段暂使用硬编码KEY）
AES_KEY = os.getenv('AES_KEY', 'cvvU2/u+x7q32CbSBVjFLdgkutBFoD90M2cr2+hIzlQ=').encode()[:32]  # 确保32字节
AES_IV = os.getenv('AES_IV', 'nFWYBd+O8o3I+M8M9/lr7g==').encode()[:16]  # 确保16字节

# 部署到服务器后修改为从base64编码的环境变量读取
# key生成 \utils\createAESkey.py   生成后保存到服务器环境变量
# AES_KEY = base64.b64decode(os.getenv('AES_KEY'))  
# AES_IV = base64.b64decode(os.getenv('AES_IV'))    

def aes_encrypt(plaintext: str) -> str:
    """AES加密（可反向解密）"""
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded_data = pad(plaintext.encode(), AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode()

def aes_decrypt(ciphertext: str) -> str:
    """AES解密"""
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    encrypted = base64.b64decode(ciphertext)
    decrypted = cipher.decrypt(encrypted)
    return unpad(decrypted, AES.block_size).decode()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decodeToken2user(token: str = Security(oauth2_scheme)):
    try:
        # 解码 JWT 令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  
        user_role: str = payload.get("role")  
        if user_id is None:
            return False
        return user_id,user_role 
    except:
        return False

