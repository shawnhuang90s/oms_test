import loguru
from pykafka import KafkaClient
from oms_test.settings import KAFKA_HOSTS, KAFKA_LOG
logger = loguru.logger
logger.add(f'{KAFKA_LOG}pykafka_test.log', format='{time} {level} {message}', level='INFO')


class PyKafkaTest:
    """Kafka 基本用法示例"""

    def __init__(self, topic_name=None, consumer_group=None, consumer_id=None):
        self.hosts = KAFKA_HOSTS
        self.client = KafkaClient(hosts=self.hosts)
        self.topic = self.client.topics[topic_name]
        self.consumer_group = consumer_group
        self.consumer_id = consumer_id

    def produce(self):
        """设置一个生产者生产消息"""
        with self.topic.get_sync_producer() as producer:
            logger.info('生产者开始生产消息 ------>')
            for i in range(5):
                producer.produce(f'测试消息 {i ** 2}'.encode())

    def consume(self):
        """设置一个消费者消费消息"""
        consumer = self.topic.get_simple_consumer(consumer_group=self.consumer_group, auto_commit_interval_ms=1,
                                                  auto_commit_enable=True, consumer_id=self.consumer_id)
        logger.info('消费者开始消费消息 <------')
        for msg in consumer:
            if msg is not None:
                logger.info(f'{msg.offset}, {msg.value.decode()}')


if __name__ == '__main__':
    kafka_obj = PyKafkaTest(topic_name='store_topic', consumer_group=b'first_consumer', consumer_id=b'first')
    kafka_obj.produce()
    kafka_obj.consume()
