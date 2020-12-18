import json
from oms_test.settings import REDIS_CONF
redis_conn = REDIS_CONF.redis_conn


def set_store_account():
    """保存店铺账户信息到 Redis 集群中"""
    store_account_key = REDIS_CONF.store_account_key
    print('======== 获取各平台店铺账户信息并保存到 Redis 集群 ========')
    for i in range(1, 21):
        # 以下数据只是测试所用, 真实数据肯定不是这样
        # Cdiscount 平台店铺账户信息
        cdiscount_dict = dict(
            username=f'username_{i}',
            password=f'password_{i}'
        )
        # Cdisount 平台店铺名称
        cd_key = f'cd_store_{i}'
        # 将店铺名与对应的账户信息保存进 Redis 中
        redis_conn.hset(cd_key, store_account_key, json.dumps(cdiscount_dict))
    print('======== 保存成功 ========')

    return


if __name__ == '__main__':
    # set_store_account()
    store_account_key = REDIS_CONF.store_account_key
    for i in range(1, 21):
        cd_key = f'cd_store_{i}'
        store_obj = redis_conn.hget(cd_key, store_account_key)
        print(store_obj)

