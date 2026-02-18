from utils.enum import ResponseCode

# 在 get_app.py 中注册异常处理器
class ManuScriptValidationMsg(Exception):
    def __init__(self, msg: str, code: int = ResponseCode.SUCCESS.value):
        self.msg = msg
        self.code = code