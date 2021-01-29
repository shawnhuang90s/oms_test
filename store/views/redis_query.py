import json
from rest_framework import status
from rest_framework.views import APIView
from oms_test.settings import REDIS_CONF
from rest_framework.response import Response


class StoreAccountView(APIView):
    """查询店铺账户信息"""
    def get(self, request):
        try:
            redis_conn = REDIS_CONF.redis_conn
            store_account_key = REDIS_CONF.store_account_key
            key = request.query_params.get("key", "")
            account_info = redis_conn.hget(store_account_key, f'test_store_{key}')
            if account_info:
                account_info = json.loads(account_info)
                return Response(data=account_info, status=status.HTTP_200_OK)
            else:
                return Response(data=f"Redis中没有店铺ID:{key} 对应的账户信息", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data=f"查询失败：{e}", status=status.HTTP_200_OK)
