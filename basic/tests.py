import loguru
from oms_test.settings import CRONTAB_LOG
logger = loguru.logger
logger.add(f'{CRONTAB_LOG}basic_tests.log', format='{time} {level} {message}', level='INFO')


def crontab_test():
    """测试定时任务"""
    logger.info(1111111111111111111)
    logger.info('这是定时任务测试...')
    logger.info(2222222222222222222)


if __name__ == '__main__':
    crontab_test()
