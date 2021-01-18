from datetime import datetime
import os, django
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms_test.settings')
django.setup()
from store.models import Store


def batch_create01():
    """批量创建店铺表测试数据（方法一）"""
    for i in range(1, 200):
        store_dict = dict(
            name=f'test_store_{i}',
            manager_name=f'test_manager_{i}',
            manager_id=i,
            center=f'test_center_{i}',
            center_id=i,
            platform=f'test_platform_{i}',
            market=f'test.{i}.com',
            market_id=i,
            status=1,
            last_download_time=datetime.now(),
        )
        print(f'新建数据：{store_dict}')
        Store.objects.create(**store_dict)

    return


def batch_create02():
    """批量创建店铺表测试数据（方法二）"""
    for i in range(1, 200):
        store_dict = dict(
            name=f'test_store_{i}',
            manager_name=f'test_manager_{i}',
            manager_id=i,
            center=f'test_center_{i}',
            center_id=i,
            platform=f'test_platform_{i}',
            market=f'test.{i}.com',
            market_id=i,
            status=1,
            last_download_time=datetime.now(),
        )
        print(f'新建数据：{store_dict}')
        try:
            Store.objects.get_or_create(**store_dict)
        except Exception as e:
            print(f'新建数据时报错：{e}')
            continue

    return


def batch_create03():
    """批量创建店铺表测试数据（方法三）"""
    store_list = list()
    for i in range(1, 200):
        store_dict = dict(
            name=f'test_store_{i}',
            manager_name=f'test_manager_{i}',
            manager_id=i,
            center=f'test_center_{i}',
            center_id=i,
            platform=f'test_platform_{i}',
            market=f'test.{i}.com',
            market_id=i,
            status=1,
            last_download_time=datetime.now(),
        )
        # print(f'新建数据：{store_dict}')
        store_list.append(Store(**store_dict))
    # batch_size 表示每次批量处理的数量
    # ignore_conflicts=True 表示忽略批量创建时的冲突
    Store.objects.bulk_create(store_list, batch_size=100, ignore_conflicts=True)

    return


if __name__ == '__main__':
    # batch_create01()
    # batch_create02()
    # batch_create03()
    r = Store.objects.first()
    print(r)
