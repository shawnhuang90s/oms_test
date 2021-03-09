import json
from oms_test.settings import REDIS_CONF

redis_conn = REDIS_CONF.redis_conn
store_account_key = REDIS_CONF.store_account_key


def save_store_account():
    """保存各平台店铺账户信息到 Redis 集群中"""

    pl = redis_conn.pipeline()
    for i in range(1, 200):
        account_dict = dict()
        store_key = f'test_store_{i}'
        ######## Cdiscount ########
        if i <= 5:
            account_dict = dict(
                username=f'username_{i}',
                password=f'password_{i}'
            )
        ######## Aliexpress ########
        elif 5 < i <= 10:
            account_dict = dict(
                app_key=f'app_key_{i}',
                access_token=f'access_token_{i}',
                secret_key=f'secret_key_{i}'
            )
        ######## Amazon ########
        elif 10 < i <= 15:
            account_dict = dict(
                ACCESS_KEY=f'ACCESS_KEY_{i}',
                SECRET_KEY=f'SECRET_KEY_{i}',
                ACCOUNT_ID=f'ACCOUNT_ID_{i}',
                MWSAuthToken=f'MWSAuthToken_{i}',
            )
        ######## Buka ########
        elif 15 < i <= 20:
            account_dict = dict(
                client_id=f'client_id_{i}',
                client_secret=f'client_secret_{i}',
                access_token=f'access_token_{i}',
                refresh_token=f'refresh_token_{i}',
            )
        ######## Daraz ########
        elif 20 < i <= 25:
            account_dict = dict(
                app_key=f'app_key_{i}',
                daraz_account=f'daraz_account_{i}',
                url=f'url_{i}',
                name=f'name_{i}',
            )
        ######## DS ########
        elif 25 < i <= 30:
            account_dict = dict(
                access_token=f'access_token_{i}',
                app_key=f'app_key_{i}',
                app_secret=f'app_secret_{i}',
            )
        ######## eBay ########
        elif 30 < i <= 35:
            account_dict = dict(
                DevID=f'DevID_{i}',
                AppID=f'AppID_{i}',
                CertID=f'CertID_{i}',
                Token=f'Token_{i}',
                RunName=f'RunName_{i}',
                OauthRefreshToken=f'OauthRefreshToken_{i}',
            )
        ######## Facebook ########
        elif 35 < i <= 40:
            account_dict = dict(
                PageID=f'PageID_{i}',
                access_token=f'access_token_{i}',
            )
        ######## JD ########
        elif 40 < i <= 45:
            account_dict = dict(
                app_key=f'app_key_{i}',
                appSecret=f'appSecret_{i}',
                access_token=f'access_token_{i}',
            )
        ######## Joom ########
        elif 45 < i <= 50:
            account_dict = dict(
                access_token=f'access_token_{i}',
                refresh_token=f'refresh_token_{i}',
                client_id=f'client_id_{i}',
                client_secret=f'client_secret_{i}',
                merchant_user_id=f'merchant_user_id_{i}',
            )
        ######## Lazada ########
        elif 50 < i <= 55:
            account_dict = dict(
                url=f'url_{i}',
                app_key=f'app_key_{i}',
                app_secret=f'app_secret_{i}',
                access_token=f'access_token_{i}',
            )
        ######## Linio ########
        elif 55 < i <= 60:
            account_dict = dict(
                user_email=f'user_email_{i}',
                app_key=f'app_key_{i}',
            )
        ######## Mercadolibre ########
        elif 60 < i <= 65:
            account_dict = dict(
                access_token_new=f'access_token_new_{i}',
                client_secret=f'client_secret_{i}',
                refresh_token_new=f'refresh_token_new_{i}',
                client_id=f'client_id_{i}',
            )
        ######## Priceminister ########
        elif 65 < i <= 70:
            account_dict = dict(
                login=f'login_{i}',
                pwd=f'pwd_{i}',
            )
        ######## Qoo10 ########
        elif 70 < i <= 75:
            account_dict = dict(
                key=f'key_{i}',
                user_id=f'user_id_{i}',
                pwd=f'pwd_{i}',
            )
        ######## Rakuten ########
        elif 75 < i <= 80:
            account_dict = dict(
                serviceSecret=f'serviceSecret_{i}',
                licenseKey=f'licenseKey_{i}',
            )
        ######## Shopee ########
        elif 80 < i <= 85:
            account_dict = dict(
                partner_id=f'partner_id_{i}',
                shop_id=f'shop_id_{i}',
                secret=f'secret_{i}',
            )
        ######## Tiki ########
        elif 85 < i <= 90:
            account_dict = dict(
                secret=f'secret_{i}',
            )
        ######## Walmart ########
        elif 90 < i <= 95:
            account_dict = dict(
                private_key=f'private_key_{i}',
                consumer_id=f'consumer_id_{i}',
                channel_type=f'channel_type_{i}',
                client_id=f'client_id_{i}',
                client_secret=f'client_secret_{i}',
            )
        ######## Wish ########
        elif 95 < i <= 100:
            account_dict = dict(
                access_token=f'access_token_{i}',
                url=f'url_{i}',
                app_key=f'app_key_{i}',
                app_secret=f'app_secret_{i}',
            )
        ######## Wowma ########
        elif 100 < i <= 105:
            account_dict = dict(
                app_key=f'app_key_{i}',
                shop_id=f'shop_id_{i}',
            )
        ######## Yahoo ########
        elif 105 < i <= 110:
            account_dict = dict(
                secret=f'secret_{i}',
                application_id=f'application_id_{i}',
                refresh_token=f'refresh_token_{i}',
                seller_id=f'seller_id_{i}',
            )
        ######## Zoodmall ########
        elif 110 < i <= 115:
            account_dict = dict(
                name=f'name_{i}',
                password=f'password_{i}',
            )
        pl.hset(store_account_key, store_key, json.dumps(account_dict))
    pl.execute()

    return


if __name__ == '__main__':
    # 保存测试数据到 Redis
    save_store_account()
    # 查看 Redis 中是否有数据
    for i in range(1, 501):
        store_key = f'test_store_{i}'
        account_info = redis_conn.hget(store_account_key, store_key)
        print(account_info)
    # 清除测试数据
    # redis_conn.flushdb()

