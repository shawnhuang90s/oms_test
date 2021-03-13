import time
import loguru
from oms_test.celery import app
from celery_once import QueueOnce
from oms_test.settings import FILE_LOG
logger = loguru.logger
logger.add(f'{FILE_LOG}celery_tasks/tasks.log', format='{time} {level} {message}', level='INFO')


@app.task(base=QueueOnce, once={'graceful': True})
def celery_test(file_path, username):
    start_time = time.time()
    fail_list = deal_excel_content(file_path, username)
    # res = record_wrong_application(fail_reason, username)
    end_time = time.time()
    time_count = end_time - start_time
    return time_count


def deal_excel_content(file_path, username):
    """处理 excel 文件内容"""
    fail_list = list()
    return fail_list
