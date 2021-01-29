from pykafka import KafkaClient


######## pykafka test ########
# 链接客户端
client = KafkaClient(hosts='127.0.0.1:9093')

# 查看已有的主题 Topic
print(client.topics)
# {b'my-replicated-topic': None}

# 查看已创建的节点
print(client.brokers)
# {
#     2: <pykafka.broker.Broker at 0x7f6169e0e650 (host=b'127.0.0.1', port=9094, id=2)>,
#     1: <pykafka.broker.Broker at 0x7f616471b390 (host=b'127.0.0.1', port=9093, id=1)>
# }
for broker in client.brokers:
    id = client.brokers[broker].id
    host = client.brokers[broker].host
    port = client.brokers[broker].port
    print(f'{id} {host.decode()}:{port}')
# 2 127.0.0.1:9094
# 1 127.0.0.1:9093

# 查看链接的节点
print(client.cluster)
# <pykafka.cluster.Cluster at 0x7f6169dfbc10 (hosts=127.0.0.1:9093)>

# 获取某个主题 Topic
topic = client.topics['my-replicated-topic']
print(topic)
# <pykafka.topic.Topic at 0x7f5ff9696e90 (name=b'my-replicated-topic')>
# 如果输入的主题不存在, 默认自动新建这个主题
new_topic = client.topics['store_topic']
print(new_topic)
# <pykafka.topic.Topic at 0x7f47493b4cd0 (name=b'store_topic')>

# 创建一个同步模式的生产者并推送消息, 只有在确认消息已发送到集群之后, 才会返回调用
# with topic.get_sync_producer() as producer:
#     for i in range(1, 4):
#         producer.produce((f'测试消息 {i ** 2}').encode())

# 创建一个消费者并接收消息
# 注意, 本文件运行多少次就会生产多少次上面的消息并在这里接收到
# 另外, 如果之前我们使用 kafka 测试时随便输入的内容在这里也会接收到
consumer = topic.get_simple_consumer()
print(consumer)
# <pykafka.simpleconsumer.SimpleConsumer at 0x7f768e032510 (consumer_group=None)>
for msg in consumer:
    if msg is not None:
        print(msg.offset, msg.value.decode())
# 0 测试消息 1
# 1 测试消息 4
# 2 测试消息 9
