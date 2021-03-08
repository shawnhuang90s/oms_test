from functools import wraps
from user.models import User
from rest_framework import status
from utils.get_username import get_username
from rest_framework.response import Response


def login_auth(func):
    """登录验证装饰器"""
    @wraps(func)
    def inner(request, *args, **kwargs):
        session_id = request.COOKIES.get('sessionid', None)
        messages = request.COOKIES.get('messages', None)
        if session_id and messages:
            return func(request, *args, **kwargs)
        else:
            return Response({'code': 0, 'desc': '请登录后再访问'}, status=status.HTTP_401_UNAUTHORIZED)

    return inner


def admin_auth(func):
    """超管校验装饰器"""
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        username = get_username(request)
        if not username:
            return Response({"code": 0, "desc": "获取用户名失败"}, status=status.HTTP_200_OK)
        user_obj = User.objects.filter(username=username).first()
        if not user_obj:
            return Response({"code": 0, "desc": "用户名不存在"}, status=status.HTTP_200_OK)
        if user_obj.is_superuser == True:
            return func(self, request, *args, **kwargs)
        else:
            return Response({"code": 0, "desc": "您没有权限执行此操作!"}, status=status.HTTP_200_OK)

    return inner
