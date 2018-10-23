import asyncio
import aiohttp
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

async def send(app, params={}):
    async with aiohttp.ClientSession() as session:
        headers = {
            'Content-Type': 'application/json'
        }
        client_url = "{}://{}:{}{}".format(
            app['config']['client']['protocol'],
            app['config']['client']['host'],
            app['config']['client']['port'],
            app['config']['client']['url']
        )
        async with session.post(client_url, headers=headers, json=params) as response:
            if response.status == 200:
                # print(await response.json())
                print("client responds ok")
            else:
                raise Exception("something went wrong")

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
    bootstrap_servers = "{}:{}".format(
        app['config']['kafka']['host'],
        app['config']['kafka']['port']
    )      
    consumer = AIOKafkaConsumer(
        app['config']['kafka']['topic'],
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