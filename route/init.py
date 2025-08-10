# 初始化路由模块，确保蓝图能被正确导入
from flask import Blueprint

# 这里不需要额外代码，仅作为包标识让Python识别routes为一个包

# routes/__init__.py​
# 确保蓝图能被正确导入​
from .books import bp as books_bp​
from .users import bp as users_bp​
from .borrows import bp as borrows_bp​
​
__all__ = ['books_bp', 'users_bp', 'borrows_bp']