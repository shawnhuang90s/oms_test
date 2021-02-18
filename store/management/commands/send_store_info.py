import os
import xlwt
import loguru
from django.db import connection
from oms_test.settings import BASE_DIR
from utils.send_email import SendEmail
from oms_test.settings import STORE_LOG
from django.core.management.base import BaseCommand
logger = loguru.logger
logger.add(f'{STORE_LOG}send_store_info.log', format='{time} {level} {message}', level='INFO')


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            send_store_info()
        except Exception as e:
            logger.error(f"发送店铺信息失败：{e}")


def send_store_info():
    """发送店铺信息到相关负责人的邮箱"""
    sql_str = "select name, manager_name, center, platform, market from oms_store where status in (1, 3, 5);"
    with connection.cursor() as cursor:
        cursor.execute(sql_str)
        store_infos = cursor.fetchall()
        logger.info(f"查询出的店铺信息：{store_infos}")
        if store_infos:
            # 新建 excel 文件
            n = 1
            file_obj = xlwt.Workbook(encoding='utf-8')
            sheet_obj = file_obj.add_sheet('data')
            sheet_obj.write(0, 0, "店铺名")
            sheet_obj.write(0, 1, "负责人")
            sheet_obj.write(0, 2, "所属中心")
            sheet_obj.write(0, 3, "所属平台")
            sheet_obj.write(0, 4, "所属市场")
            # 将重复订单信息写入 excel 文件
            for obj in store_infos:
                name, manager_name, center, platform, market = obj
                sheet_obj.write(n, 0, str(name))
                sheet_obj.write(n, 1, str(manager_name))
                sheet_obj.write(n, 2, str(center))
                sheet_obj.write(n, 3, str(platform))
                sheet_obj.write(n, 4, str(market))
                logger.info(f"********* 已将第 {n} 条符合条件的订单信息保存进 excel 文件中 **********")
                n += 1

            if n > 1:
                file_path = f"{BASE_DIR}/store_infos.xls"
                file_obj.save(file_path)
                content = f"""Hi, all:
                附件是店铺相关信息
                相关详情烦请查看 excel 文件, 谢谢!"""
                SendEmail(
                    user='输入发送者的邮箱账号',
                    password='输入发送者的邮箱账号密码',
                    to_list=['接收者的邮箱账号(可以是同一个)'],
                    tag=f'店铺信息整理',
                    content={
                        'content': content,
                        'type': 'plain',
                        'coding': 'utf-8'
                    },
                    doc=file_path
                ).send()
                # 发送邮件后将其删除
                os.remove(file_path)


if __name__ == '__main__':
    send_store_info()
