from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio

kafka_cluster = "esb.u2035dev.ru:9092"
kafka_topic = "carrier-test"

async def produce(loop, msg):
    producer = AIOKafkaProducer(
        loop=loop,
        bootstrap_servers=kafka_cluster
    )
    await producer.start()
    try:
        await producer.send_and_wait(kafka_topic, msg.encode())
    finally:
        await producer.stop()

async def consume(app):
    consumer = AIOKafkaConsumer(
        kafka_topic,
        loop=app.loop, 
        bootstrap_servers=kafka_cluster,
    )
    await consumer.start()
    try:
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        await consumer.stop()