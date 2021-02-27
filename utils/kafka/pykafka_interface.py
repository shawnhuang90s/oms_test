import json
import loguru
from pykafka import KafkaClient
from oms_test.settings import KAFKA_HOSTS, KAFKA_LOG
from pykafka.exceptions import SocketDisconnectedError, LeaderNotAvailable
logger = loguru.logger
logger.add(f'{KAFKA_LOG}pykafka_interface.log', format='{time} {level} {message}', level='INFO')


class PykafkaInterface:
    """kafka 连接"""

    def __init__(self, topic):
        self.hosts = KAFKA_HOSTS
        self.client = KafkaClient(hosts=self.hosts)
        self.topic = self.client.topics[topic]


class ProducerInterface(PykafkaInterface):
    """生产者接口"""

    def __init__(self, topic):
        super().__init__(topic)
        self.producer = self.topic.get_sync_producer()

    def send(self, msg):
        """生产者生产消息"""
        try:
            msg = json.dumps(msg)
            self.producer.produce(msg.encode('utf-8'))
            logger.info(f'发送消息：{msg} 成功!')
        except (SocketDisconnectedError, LeaderNotAvailable):
            # self.producer.start()
            logger.warning(f'生产者生成消息时报错, 正在尝试重启生产者')
            self.producer.stop()
            self.producer.start()
            msg = json.dumps(msg)
            self.producer.produce(msg.encode('utf-8'))
        except Exception as e:
            logger.info(f'生产者生产消息时报错：{e}')


class ConsumerInterface(PykafkaInterface):
    """消费者接口"""

    def __init__(self, topic, consumer_group, consumer_id):
        super().__init__(topic)
        self.consumer_group = consumer_group
        self.consumer_id = consumer_id
        self.consumer = self.topic.get_simple_consumer(consumer_group=self.consumer_group, auto_commit_interval_ms=1,
                                                       auto_commit_enable=True, consumer_id=self.consumer_id)

    def handle(self, msg, func):
        """处理消费的消息"""
        logger.info(f'offset:{msg.offset} | value:{msg.value} | partitions:{self.consumer.partitions}')
        return func(json.loads(msg.value.decode('utf-8')))

    def receive(self, func):
        """消费消息"""
        try:
            for msg in self.consumer:
                if msg:
                    self.handle(msg, func)
        except SocketDisconnectedError:
            logger.warning(f'消费消息时报错, 正在尝试重启消费者')
            self.consumer.stop()
            self.consumer.start()
        except Exception as e:
            logger.warning(f'消费消息时报错：{e}')


def test(msg):
    print(f'实时接收消息：{msg}')
    return


if __name__ == '__main__':
    producer = ProducerInterface(topic='store_topic')
    producer.send('this is a test...')
    consumer = ConsumerInterface(topic='store_topic', consumer_group=b'first_consumer', consumer_id=b'first')
    consumer.receive(func=test)
