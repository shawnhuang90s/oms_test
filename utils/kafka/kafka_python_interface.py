import random
import loguru
import asyncio
from oms_test.settings import KAFKA_LOG, KAFKA_HOSTS
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
logger = loguru.logger
logger.add(f'{KAFKA_LOG}kafka_python_interface.log', format='{time} {level} {message}', level='INFO')


class KafkaProductInterface:
    """kafka 生产者接口"""

    def __init__(self, topic=None):
        self.hosts = KAFKA_HOSTS
        self.topic = topic
        self.msg_list = list()
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            self.loop = asyncio.get_event_loop()

    def put(self, msg):
        """将消息放进列表中"""
        self.msg_list.append(msg)

    async def produce_msg(self):
        """启动生产者并发送消息"""
        # 定义一个生产者
        producer = AIOKafkaProducer(loop=self.loop, bootstrap_servers=self.hosts)
        await producer.start()

        copied_list = self.msg_list.copy()
        # 每次发送消息之后, 把原列表的内容清空, 避免发送重复的消息
        self.msg_list = list()
        try:
            batch = producer.create_batch()
            for msg in copied_list:
                metadata = batch.append(key=None, value=msg.encode('utf-8'), timestamp=None)
                if metadata is None:
                    partitions = await producer.partitions_for(self.topic)
                    partition = random.choice(tuple(partitions))
                    await producer.send_batch(batch, self.topic, partition=partition)
                    logger.warning(f'发送 {batch.record_count()} 条消息到 topic:{self.topic}, partition:{partition}')
                    batch = producer.create_batch()
            partitions = await producer.partitions_for(self.topic)
            partition = random.choice(tuple(partitions))
            await producer.send_batch(batch, self.topic, partition=partition)
            logger.warning(f'发送 {len(copied_list)} 条消息：{copied_list} 到主题：[{self.topic}], partition:{partition}')
        finally:
            # 等待所有待发消息被发送出去或者过期
            await producer.stop()

    def create_task(self):
        """创建任务"""
        try:
            if self.loop.is_running():
                self.loop.create_task((self.produce_msg()))
            else:
                self.loop.run_until_complete(self.produce_msg())
        except Exception as e:
            logger.error(f'kafka 生产者事件循环时发生异常：{e}')

    def send(self, msg):
        """发送消息接口"""
        try:
            self.put(msg)
            self.create_task()
        except Exception as e:
            logger.error(f'kafka 发送消息：{msg} 失败：{e}')


class KafkaConsumerInterface:
    """kafka 消费者接口"""

    def __init__(self, topic):
        self.topic = topic
        self.hosts = KAFKA_HOSTS
        self.loop = asyncio.get_event_loop()

    def deal_with_msg(self, msg):
        """处理消费者接收的消息"""
        pass

    async def consumer_msg(self):
        """消费消息"""
        # 定义一个消费者
        consumer = AIOKafkaConsumer(
            self.topic,
            group_id='store_account',
            loop=self.loop,
            bootstrap_servers=KAFKA_HOSTS,
            session_timeout_ms=2 * 10000,
            heartbeat_interval_ms=2 * 3000,
            max_partition_fetch_bytes=15 * 1024 * 1024
        )
        await consumer.start()
        try:
            async for message in consumer:
                msg = message.value.decode('utf-8')
                logger.info(f'偏移量：{message.offset} 消息：{msg}')
                self.deal_with_msg(msg)
        except Exception as e:
            logger.error(f'消费 kafka 消息时报错：{e}')
        finally:
            await consumer.stop()

    def receive(self):
        """接收消息接口"""
        try:
            logger.warning('======== kafka 消费者事件循环开启 ========')
            if self.loop.is_running():
                self.loop.create_task(self.consumer_msg())
            else:
                self.loop.create_task(self.consumer_msg())
                self.loop.run_forever()
        finally:
            logger.warning('======== kafka 消费者事件循环结束 ========')


if __name__ == '__main__':
    producer = KafkaProductInterface(topic='store_topic')
    producer.send(msg='this is a test...')
    consumer = KafkaConsumerInterface(topic='store_topic')
    consumer.receive()
