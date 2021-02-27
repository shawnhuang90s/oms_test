import loguru
from datetime import datetime
from oms_test.settings import KAFKA_LOG
from utils.mysql.mysql_interface import PyMySQLPool
from utils.kafka.pykafka_interface import ProducerInterface, ConsumerInterface

logger = loguru.logger
logger.add(f'{KAFKA_LOG}store_kafka.log', format='{time} {level} {message}', level='INFO')


def save_account_info(account_msg=None):
    """将消费者获取的店铺账户信息保存到表中"""
    if account_msg and isinstance(account_msg, dict):
        if account_msg['table'] == 'oms_store':
            account_list = account_msg.get('account_list', [])
            if account_list and isinstance(account_list, list):
                for account_tuple in account_list:
                    # 这里注意：虽然我们在生产者推送消息时每个店铺信息放在元组中, 但 json.dumps(msg) 之后, 元组会变成列表
                    if isinstance(account_tuple, list):
                        account_tuple = tuple(account_tuple)
                    try:
                        mysql_conn = PyMySQLPool(config_filename='oms_db.cnf', conf_name='dbMysql')
                        name, manager_name, manager_id, center, center_id, platform, market, market_id, status, last_download_time = account_tuple
                        account_sql = f"REPLACE INTO oms_store (name, manager_name, manager_id, center, center_id, platform, market, market_id, status, last_download_time) VALUES (\'{name}\', \'{manager_name}\', \'{manager_id}\', \'{center}\', \'{center_id}\', \'{platform}\', \'{market}\', \'{market_id}\', \'{status}\', \'{last_download_time}\');"
                        mysql_conn.replace(account_sql)
                        logger.info(f'将数据：{account_tuple} 保存到 oms_store 表中成功！')
                        mysql_conn.dispose()
                    except Exception as e:
                        logger.warning(f'将数据：{account_tuple} 保存到 oms_store 表中失败：{e}')
                        continue


def produce_store_account():
    """店铺账户信息实时推送"""
    try:
        producer = ProducerInterface(topic='store_topic')
        account_msg = {'table': 'oms_store', 'account_list': []}
        for i in range(200, 501):
            # oms_store 字段：name, manager_name, manager_id, center, center_id, platform,
            # market, market_id, status, last_download_time
            account_tuple = (
                f'test_store_{i}', f'test_manager_{i}', i, f'test_center_{i}', i, f'test_platform_{i}',
                f'test_market_{i}', i, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            account_msg['account_list'].append(account_tuple)
        producer.send(account_msg)
    except Exception as e:
        logger.warning(f'推送店铺账户信息到 kafka 失败：{e}')


def consume_store_account():
    """店铺账户信息实时接收"""
    try:
        consumer = ConsumerInterface(topic='store_topic', consumer_group=b'first_test', consumer_id=b'first')
        consumer.receive(func=save_account_info)
    except Exception as e:
        logger.warning(f'从 kafka 获取店铺账户信息失败：{e}')


if __name__ == '__main__':
    produce_store_account()
    consume_store_account()
