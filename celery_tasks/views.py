import os
import loguru
from .tasks import celery_test
from django.db import connection
from django.http import FileResponse
from rest_framework.views import APIView
from utils.get_username import get_username
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from oms_test.settings import FILE_LOG, UPLOAD_ROOT, DOWNLOAD_ROOT
from utils.decorator_func import admin_auth, login_auth, permission_auth
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_206_PARTIAL_CONTENT, HTTP_202_ACCEPTED
logger = loguru.logger
logger.add(f'{FILE_LOG}test.log', format='{time} {level} {message}', level='INFO')


class DealExcelInfoView(APIView):
    """使用分布式队列处理 excel 文件示例"""

    # @method_decorator(login_auth)
    def get(self, request):
        """下载模板或excel处理结果接口"""
        # username = get_username(request)
        username = 'admin'
        file_name = request.query_params.get("file_name", None)
        # task_id 作为标识符判断文件是否还在处理或是否已下载
        task_id = request.query_params.get("task_id", None)
        file_path = os.path.join(DOWNLOAD_ROOT, file_name)
        try:
            # 用户上传 excel 文件后, 服务器处理该文件, 并且返回一个 task_id 给前端
            # 用户点击下载处理结果时, 前端会将 task_id 再返回给后端
            # 我们之前已经安装了 django_celery_results 包, 这样可以根据 task_id 去查对应的任务是否已经处理完成
            if task_id:
                # 去数据库查询对应任务id的执行结果; 如果没查到说明任务尚未执行完
                cursor = connection.cursor()
                sql = f"SELECT result FROM django_celery_results_taskresult WHERE task_id={task_id};"
                cursor.execute(sql)
                result = cursor.fetchone()
                # 如果用户点击下载处理结果, 服务器还没有该文件, 而且任务表查不到任务的结果, 说明该文件还在处理中
                if not (os.path.exists(file_path) and result):
                    data = {'code': 0, 'desc': '您上传的 excel 还在处理中, 请稍后再下载处理结果'}
                    return Response(data, status=HTTP_204_NO_CONTENT)
                # 如果用户点击下载处理结果, 服务器还没有该文件, 但是任务表能找到对应任务的结果, 说明该文件已经处理完
                # 并且用户之前已经下载过处理结果了, 而我们要做的是用户第一次下载结果后就会在服务器删除该文件, 用户不能再次下载
                elif not os.path.exists(file_path) and result:
                    data = {'code': 0, 'desc': '您已下载过处理结果, 服务器已删除该文件'}
                    return Response(data, status=HTTP_206_PARTIAL_CONTENT)
            # 如果前端没有传 task_id, 有两种情况：
            # 1. 用户点击的是下载模板文件
            # 2. 用户之前已经下载过处理结果, 再次点击时应该提示已经下载过了
            # 当然, 也可以把下载模板文件和处理结果文件分两个接口来处理
            else:
                if not os.path.exists(file_path):
                    data = {'code': 0, 'desc': '模板文件未找到, 或您已下载过处理结果'}
                    return Response(data, status=HTTP_202_ACCEPTED)

            # 用户下载模板或处理结果正常时的处理
            response = FileResponse(open(file_path, "rb"))
            # response 标识该返回内容为文件格式
            response['Content-Type'] = 'application/octet-stream'
            response['Content-Disposition'] = f'attachment;filename={file_name}'
            # 模板文件在服务器中一直保留, 但是处理结果文件一旦下载就删除
            if file_name != "测试模板文件.xls" and os.path.exists(file_path):
                os.remove(file_path)
            return response
        except Exception as e:
            logger.info(f"用户：{username} 下载模板或处理结果时报错：{e}")
            data = {'code': 0, 'desc': f'下载模板文件或处理结果失败：{e}'}
            return Response(data)

    # @method_decorator(permission_auth)
    # @method_decorator(admin_auth)
    # @method_decorator(login_auth)
    def post(self, request):
        try:
            # username = get_username(request)
            username = 'admin'
            file_obj = request.FILES.get('file_name', None)
            if not file_obj:
                return Response(data={'code': 0, 'desc': '获取不到文件对象'})
            logger.info(f'用户：{username} 本次上传的文件为：{file_obj}')
            file_name = file_obj.name
            if not (file_name.endswith('.xls') or file_name.endswith('.xlsx')):
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
            # 分块写入文件, 使用 chunks() 代替 read() 可以在读取大文件时尽量减少对系统内存的占用
            with open(file_path, 'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

            # 保存文件后, 将其放到任务队列进行异步处理
            # 注意, 前面已经提到, 这里不使用 .delay() 方法
            task = celery_test.apply_async(args=(file_path, username))
            # 这里把 task.id 传给前端, 目的是
            return Response(data={'code': 1, 'desc': 'excel文件上传成功, 请稍后查看具体进度', 'task': task.id})
        except Exception as e:
            logger.info(f'处理测试文件失败：{e}')
            return Response(data={'code': 0, 'desc': f'处理测试文件失败：{e}'})
