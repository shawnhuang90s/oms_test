import random
import loguru
import asyncio
from django.db import connections
from oms_test.settings import KAFKA_LOG, KAFKA_HOSTS
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
logger = loguru.logger
logger.add(f'{KAFKA_LOG}kafka_python_interface.log', format='{time} {level} {message}', level='INFO')


class KafkaConsumerInterface:
    """kafka 消费者接口"""

    def __init__(self):
        self.tasks = list()
        self.hosts = KAFKA_HOSTS
        self.loop = asyncio.get_event_loop()

    async def _consume_msg(self, msg):
        """消费并处理消息, 如果过程出错导致连接断开则重试"""
        try:
            pass
            logger.warning(f'kafka 消费消息：{msg} 成功')
        except RuntimeError as e:
            logger.error(f'kafka 消费消息：{msg} 时失败：{e}')
        except Exception as e:
            if str(e).__contains__('MySQL server has gone away'):
                # 如果 MySQL 服务器断开, 则尝试再次连接主库
                connections['default'].close_if_unusable_or_obsolete()
                # 再次消费消息
                await asyncio.wait({self._consume_msg(msg)})
            else:
                logger.error(f'kafka 消费消息：{msg} 时失败：{e}')

    async def _run(self, consumer):
        """启动消费者消费 kafka 中的消息"""
        await consumer.start()
        try:
            async for message in consumer:
                msg = message.value.decode('utf-8')
                logger.info(f'偏移量：{message.offset} 消息：{msg}')
                await asyncio.wait({self._consume_msg(msg)})
        except Exception as e:
            logger.error(f'消费 kafka 消息时报错：{e}')
        finally:
            await consumer.stop()

    async def join(self, topics):
        """将 kafka 消费者加入事件循环"""
        for topic in topics:
            print(111111111111111111)
            print(topic)
            print(self.loop)
            consumer = AIOKafkaConsumer(
                topic,
                group_id='store',
                loop=self.loop,
                bootstrap_servers=KAFKA_HOSTS,
                # session_timeout_ms=2*10000,
                # heartbeat_interval_ms=2*3000,
                # max_partition_fetch_bytes=15*1024*1024
            )
            print(2222222222222222222222)
            self.tasks.append(self._run(consumer))

    def run(self):
        """开启 kafka 事件循环"""
        try:
            logger.warning('======== kafka 消费者事件循环开启 ========')
            if self.loop.is_running():
                self.loop.create_task(asyncio.wait(self.tasks))
            else:
                self.loop.create_task(asyncio.wait(self.tasks))
                self.loop.run_forever()
        finally:
            logger.warning('======== kafka 消费者事件循环结束 ========')


class KafkaProductInterface:
    """kafka 生产者接口"""

    def __init__(self, topic_name):
        self.hosts = KAFKA_HOSTS
        self.topic = topic_name
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

    async def _send(self, msg):
        """发送消息"""
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
            logger.warning(f'发送 {len(copied_list)} 条消息：{copied_list} 到 topic:{self.topic}, partition:{partition}')
        finally:
            # 等待所有待发消息被发送出去或者过期
            await producer.stop()

    def send(self, msg):
        """异步发送消息入口, 适用高并发场景"""
        try:
            if self.loop.is_running():
                self.loop.create_task((self._send(msg)))
            else:
                self.loop.run_until_complete(self._send(msg))
        except Exception as e:
            logger.error(f'kafka 生产者事件循环时发生异常：{e}')

    def sync_send(self, msg):
        """同步发送消息入口, 适用低并发场景"""
        try:
            self.put(msg)
            self.send(msg)
        except Exception as e:
            logger.error(f'kafka 发送消息：{msg} 失败：{e}')


if __name__ == '__main__':
    producer = KafkaProductInterface('store_topic')
    producer.sync_send('这是一次测试')
    consumer = KafkaConsumerInterface()
    consumer.join(['store_topic'])
    consumer.run()
