from enum import Enum

# name 描述, value 状态码
class ResponseCode(Enum):
    """
    项目接口返回状态码管理
    """
    SUCCESS = 200  # 接口正常返回
    CLIENT_ERROR = 400  # 客户端错误
    SERVER_ERROR = 500  # 服务端错误
    
