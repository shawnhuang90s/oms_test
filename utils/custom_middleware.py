import json
import time
import loguru
from datetime import datetime
from oms_test.settings import OMS_LOG
from utils.get_username import get_username
from django.utils.deprecation import MiddlewareMixin
logger = loguru.logger
logger.add(f'{OMS_LOG}custom_middleware.log', format='{time} {level} {message}', level='INFO')


class LoggerMiddleware(MiddlewareMixin):
    """自定义日志中间件"""

    def process_request(self, request):
        """请求信息"""
        start_time = time.time()
        request_data = {"开始时间": start_time}
        if request.GET.dict():
            request_data["query_params"] = request.GET.dict()
        if request.body:
            try:
                request_data["data"] = json.loads(request.body.decode("utf8", "ignore"))
            except:
                request_data["data"] = request.body.decode("utf8", "ignore")
        logger.info(f'请求参数：{request_data}')

        # 每次请求的用户信息输入日志
        session_id = request.COOKIES.get('sessionid')
        # username = request.COOKIES.get('username')
        if session_id:
            username = get_username(request)
            action_time = datetime.now()
            action_time = datetime.strftime(action_time, "%Y-%m-%dT%H:%M:%S+08:00")
            url = request.path_info
            sys_data = {"system": "oms_test", "action_time": action_time, "uri": url,
                        "name": username, "sid": session_id}
            logger.info(f'用户信息参数:{sys_data}')
        return

    def process_response(self, request, response):
        """响应信息"""
        end_time = time.time()
        response_data = {"结束时间": end_time}
        try:
            content = response.content.decode()
            response_data["data"] = json.loads(content)
        except:
            response_data["data"] = []
        logger.info(f'响应参数：{response_data}')
        return response
