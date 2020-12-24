from user.models import User
from rest_framework.settings import api_settings
from rest_framework.permissions import BasePermission


class APIPermission(BasePermission):
    """访问API接口需要权限验证"""

    def has_permission(self, request, view):
        try:
            # print(request.user)
            User.objects.get(username=request.user)
        except User.DoesNotExist:
            # 目前表里没添加数据, 默认都可以访问
            return True
        return False


# class IsIdempotent(BasePermission):
#     # message = 'Duplicate request detected.'
#     message = '短时间内的操作过于频繁'
#
#     def get_ident(self, request):
#         """
#         Identify the machine making the request by parsing HTTP_X_FORWARDED_FOR
#         if present and number of proxies is > 0. If not use all of
#         HTTP_X_FORWARDED_FOR if it is available, if not use REMOTE_ADDR.
#         """
#         xff = request.META.get('HTTP_X_FORWARDED_FOR')
#         remote_addr = request.META.get('REMOTE_ADDR')
#         num_proxies = api_settings.NUM_PROXIES
#         if num_proxies is not None:
#             if num_proxies == 0 or xff is None:
#                 return remote_addr
#             addrs = xff.split(',')
#             client_addr = addrs[-min(num_proxies, len(addrs))]
#             return client_addr.strip()
#         return ''.join(xff.split()) if xff else remote_addr
