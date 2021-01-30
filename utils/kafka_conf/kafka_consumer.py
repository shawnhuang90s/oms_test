import loguru
from pykafka import KafkaClient
from oms_test.settings import KAFKA_LOG, KAFKA_HOST, KAFKA_PORT

logger = loguru.logger
logger.add(f'{KAFKA_LOG}kafka_test.log', format='{time} {level} {message}', level='INFO')


class SimpleConsumer:

    def __init__(self):
        self.host = KAFKA_HOST
        self.port = KAFKA_PORT

    def run(self):
        logger.info('=============== kafka consumer start ===============')
        client = KafkaClient(hosts=f'{self.host}:{self.port}')


if __name__ == '__main__':
    c_obj = SimpleConsumer()
    c_obj.run()
