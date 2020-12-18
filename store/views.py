from rest_framework import status
from oms_test.settings import REDIS_CONF
from rest_framework.views import APIView
from rest_framework.response import Response


class QueryRedis(APIView):
    """Redis 查询接口"""

    def get(self, request):
        try:
            conn = REDIS_CONF.r_client
            # 从请求的 URL 中获取对应信息
            key = request.query_params.get('key', '')
            type = request.query_params.get('type', '').lower()
            hkey = request.query_params.get('hkey', '')

            # 如果是查询哈希类型的值
            if type == 'hash':
                pass
                # if hkey ==

        except Exception as e:
            return Response(data={'msg': f'查询失败：{e}'}, status=status.HTTP_200_OK)
