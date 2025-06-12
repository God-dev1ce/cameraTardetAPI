from schemas.response import ResponseModel

def success_response(data=None, msg="操作成功"):
    return ResponseModel(code=200, msg=msg, data=data)

def error_response(code=400, msg="操作失败"):
    return ResponseModel(code=code, msg=msg)