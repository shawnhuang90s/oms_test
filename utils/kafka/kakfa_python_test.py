import loguru
import asyncio
from oms_test.settings import KAFKA_LOG, KAFKA_HOSTS
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
logger = loguru.logger
logger.add(f'{KAFKA_LOG}kafka_python_test.log', format='{time} {level} {message}', level='INFO')


class KafkaPythonTest:

    def __init__(self, topic_name=None, group_id=None):
        self.topic_name = topic_name
        self.group_id = group_id
        self.hosts = KAFKA_HOSTS
        self.loop = asyncio.get_event_loop()

    def produce(self):
        """生产者测试"""
        async def producer_obj():
            """定义一个生产者"""
            producer = AIOKafkaProducer(
                loop=self.loop,
                bootstrap_servers=self.hosts
            )
            await producer.start()
            try:
                produce_msg = '实时消息测试'
                # 选择某个主题
                await producer.send_and_wait(self.topic_name, produce_msg.encode())
                logger.info(f'生产者发送消息："{produce_msg}" 成功!')
            except Exception as e:
                logger.info(f'生产者发送消息失败：{e}')
            finally:
                await producer.stop()

        self.loop.run_until_complete(producer_obj())

        return

    def consume(self):
        """消费者测试"""
        async def consumer_obj():
            """定义一个消费者"""
            consumer = AIOKafkaConsumer(
                self.topic_name,
                loop=self.loop,
                bootstrap_servers=self.hosts,
                # 设置一个 group_id, 这样这个消费者只消费一次消息, 不重复消费
                group_id=self.group_id
            )
            await consumer.start()
            try:
                async for msg in consumer:
                    # print(f'consumed: {msg.topic}, {msg.partition}, {msg.offset}, {msg.key}, {msg.value.decode()}, {msg.timestamp}')
                    logger.info(f'消费者接收消息："{msg.value.decode()}" 成功!')
            except Exception as e:
                logger.info(f'消费者接收消息失败：{e}')
            finally:
                await consumer.stop()

        self.loop.run_until_complete(consumer_obj())

        return


if __name__ == '__main__':
    # 注意：因为 kafka 的生产与消费都是实时的, 因此必须先让生产者实时发送一条消息, 这样消费者才能实时接收到
    # 如果不开启生产者发送消息, 消费者会一直等着接收生产者实时发送的消息, 只要生产者不发送消息, 消费者就会一直等着, 不会结束运行
    kafka_obj = KafkaPythonTest(topic_name='store_topic', group_id='first_group')
    kafka_obj.produce()
    kafka_obj.consume()








