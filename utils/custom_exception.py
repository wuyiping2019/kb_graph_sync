import json
import cx_Oracle
from selenium.common import NoSuchElementException
from utils.common_utils import extract_bracket_content


def raise_exception(error, **kwargs):
    # 如果报错属于oracle的报错
    if isinstance(error, cx_Oracle.DatabaseError):
        if error.args[0].code == 904:
            raise CustomException(1, 'oracle中执行插入操作,插入的字段不存在')
        else:
            raise error
    # json.loads报错
    elif isinstance(error, json.JSONDecodeError):
        if error.colno == 2:
            raise CustomException(2, '解析json异常')
        if error.colno == 1:
            raise CustomException(4, '解析的字符串并非json格式')
    # dict无法获取不存在的key值
    elif isinstance(error, KeyError):
        error_key = error.args[0]
        raise CustomException(3, f'字典不存在"{error_key}"的key值')
    # driver.find_element无法找到目标元素时报错
    elif isinstance(error, NoSuchElementException):
        content = extract_bracket_content(error.args[0])
        raise CustomException(5, f'无法定位到元素{content}')
    else:
        raise error


def cast_exception(error, **kwargs):
    try:
        raise_exception(error, **kwargs)
    except Exception as e:
        return e


class CustomException(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __repr__(self):
        return f'CustomException({self.code, self.msg})'

    def __str__(self):
        return f'CustomException({self.code, self.msg})'
