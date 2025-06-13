from fastapi.responses import JSONResponse
from schemas.response import ResponseModel

def success_response(data=None, msg="操作成功"):
    return JSONResponse(
        status_code=200,
        content={
            "code": 200,
            "msg": msg,
            "data": data
        }
    )

def error_response(code=400, msg="操作失败"):
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "msg": msg,
            "data": None
        }
    )