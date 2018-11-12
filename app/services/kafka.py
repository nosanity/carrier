import aiohttp
from app import Producer
from aiokafka import AIOKafkaConsumer
from app.services import failed_messages

async def produce(app, topic, msg):
    producer = Producer.get_producer(app.loop, app['config'])
    await producer.start()
    try:
        await producer.send_and_wait(topic, str(msg).encode())
    except Exception:
        await producer.stop()

async def send_to_consumer(app, consumer, params, resend=0):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(consumer['url'], headers=consumer['headers'], json=params) as response:
                if response.status != 200:
                    raise Exception("HTTP not OK")
                return True
    except Exception:
        await failed_messages.handle_failed_message(app['db'], params, consumer, resend)
        return False

async def notify_consumers(app, params={}):
    for consumer in app['consumers']:
        await send_to_consumer(app, consumer, params)

async def consume(app):
    topics = tuple(app['config']['kafka']['topics'])
    bootstrap_servers = "{}:{}".format(
        app['config']['kafka']['host'],
        app['config']['kafka']['port']
    )      
    consumer = AIOKafkaConsumer(
        *topics,
        loop=app.loop, 
        bootstrap_servers=bootstrap_servers,
    )
    await consumer.start()
    try:
        async for msg in consumer:
            if app['config']['debug']:
                print("Incoming message: ", msg.topic, msg.partition, msg.offset, msg.key, msg.value, msg.timestamp)
            params = {
                'topic': msg.topic,
                'partition': msg.partition,
                'offset': msg.offset,
                'key': msg.key, 
                'value': msg.value.decode("utf-8"),
                'timestamp': msg.timestamp
            }
            await notify_consumers(app, params)
    finally:
        await consumer.stop()