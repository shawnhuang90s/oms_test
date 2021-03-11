import os
import loguru
from rest_framework.views import APIView
from utils.get_username import get_username
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from oms_test.settings import FILE_LOG, UPLOAD_ROOT, DOWNLOAD_ROOT
from utils.decorator_func import admin_auth, login_auth, permission_auth
logger = loguru.logger
logger.add(f'{FILE_LOG}test.log', format='{time} {level} {message}', level='INFO')


class DealExcelInfoView(APIView):
    """使用分布式队列处理 excel 文件示例"""

    @method_decorator(permission_auth)
    @method_decorator(admin_auth)
    @method_decorator(login_auth)
    def post(self, request):
        try:
            username = get_username(request)
            file_obj = request.FILES.get('file_name', None)
            if not file_obj:
                return Response(data={'code': 0, 'desc': '获取不到文件对象'})
            logger.info(f'用户：{username} 本次上传的文件为：{file_obj}')
            file_name = file_obj.name
            if not file_name.endswith('.xls', '.xlsx'):
                return Response(data={'code': 0, 'desc': '请上传后缀为 .xls 或 .xlsx 的 excel 文件!'})
            # 重新拼接文件名, 假设文件名 file_test.xls
            file_info = file_name.split('.')  # ['file_test', 'xls']
            new_file_name = f'{file_info[0]}_{username}.{file_info[1]}'
            # 检查目录是否存在, 不存在则新建
            if not os.path.exists(UPLOAD_ROOT):
                os.makedirs(UPLOAD_ROOT)
            file_path = os.path.join(UPLOAD_ROOT, new_file_name)
            # 假设之前已经上传了一份文件, 但用户没有下载处理结果的 excel 文件, 则给出提示
            ret_file_path = f'{DOWNLOAD_ROOT}测试数据处理结果_{username}.xls'
            if os.path.exists(ret_file_path):
                return Response(data={'code': 0, 'desc': '请先下载之前上传文件后的处理结果!'})

        except Exception as e:
            logger.info(f'处理测试文件失败：{e}')
