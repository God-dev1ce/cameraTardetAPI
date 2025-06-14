from Crypto.Random import get_random_bytes
import base64

# 生成并打印密钥（仅需运行一次）
key = get_random_bytes(32)  # AES-256
iv = get_random_bytes(16)   # CBC IV

print(f"请设置环境变量：")
print(f"AES_KEY={base64.b64encode(key).decode()}")
print(f"AES_IV={base64.b64encode(iv).decode()}")