import asyncio
import aiohttp
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

async def handle_client_response(response):
    # await response.json()
    if response.status != 200:
        # TODO What to do when message wasn't delivered?
        raise Exception("something went wrong")

async def send(app, params={}):
    async with aiohttp.ClientSession() as session:
        for consumer in app['consumers']:
            async with session.post(consumer['url'], headers=consumer['headers'], json=params) as response:
                await handle_client_response(response)

async def produce(app, topic, msg):
    bootstrap_servers = "{}:{}".format(
        app['config']['kafka']['host'],
        app['config']['kafka']['port']
    )    
    producer = AIOKafkaProducer(
        loop=app.loop,
        bootstrap_servers=bootstrap_servers
    )
    await producer.start()
    try:
        await producer.send_and_wait(topic, msg.encode())
    finally:
        await producer.stop()

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
            print("consumed: ", msg.topic, msg.partition, msg.offset, msg.key, msg.value, msg.timestamp)
            params = {
                'topic': msg.topic,
                'partition': msg.partition,
                'offset': msg.offset,
                'key': msg.key, 
                'value': msg.value.decode("utf-8"),
                'timestamp': msg.timestamp
            }
            await send(app, params)
    finally:
        await consumer.stop()