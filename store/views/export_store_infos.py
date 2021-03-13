import os
import django
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')
django.setup()
import xlwt
from datetime import datetime
from store.models import Store
from collections import OrderedDict
from oms_test.settings import DOWNLOAD_ROOT
from store.serializers import StoreInfoSerializer
from utils.fields_verbose_name import get_fields_verbose_name
from utils.excel_config import set_excel_style, export_to_file


def export_test():
    """测试数据导出到 excel 文件功能"""
    try:
        store_infos = Store.objects.all()
        # 假设数据量太大, 可使用切片方式设置每次导出的数据, 比如第一次[:101], 第二次[101:201]...
        # store_infos = store_infos[:10001]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name = f"测试数据导出功能_admin_{current_time}.xls"
        # file_path = os.path.join(DOWNLOAD_ROOT, 'test_files/')
        # if not os.path.exists(file_path):
        #     os.makedirs(file_path)
        file_path = os.path.join(DOWNLOAD_ROOT, file_name)
        serializer = StoreInfoSerializer(store_infos, many=True)
        # 设置表头和内容样式
        head_style = set_excel_style(color='light_orange', name=u'微软雅黑', bold=True, height=240)
        value_style = set_excel_style(height=180, horz=xlwt.Alignment.HORZ_LEFT)
        # 表头字段内容
        header_mapping = get_fields_verbose_name('store', 'Store')
        header_mapping = OrderedDict(header_mapping)
        export_to_file(header_style=head_style, value_style=value_style, data_dict=serializer.data,
                       header_map=header_mapping, file_path=file_path, sheet_name='店铺账户信息')
        print('导出数据成功, 请查看 oms_test/files/download/ 路径下是否已经生成对应的文件!')
    except Exception as e:
        print(f'导出数据失败：{e}')


if __name__ == '__main__':
    export_test()
