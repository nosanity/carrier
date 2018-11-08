import base64
import asyncio
import aiohttp
from aiokafka import AIOKafkaConsumer
from app import Producer
from app.db import insert

async def insert_failed_message(pool, msg):
    query = [
        "INSERT INTO message_failed_to_send VALUES (NULL, ",
        "'{}', '{}', '{}', '{}', '{}', '{}'".format(
            msg['topic'], 
            msg['partition'],
            msg['offset'],
            base64.b64encode(msg['value'].encode()).decode("utf-8"),
            msg['key'],
            msg['timestamp'],
        ),
        ", DEFAULT, NOW(), NOW());"
    ]
    await insert(pool, "".join(query))

async def handle_client_response(pool, response):
    if response.status != 200:
        if app['config']['debug']:
            await insert_failed_message(pool, params)

async def send(app, params={}):
    async with aiohttp.ClientSession() as session:
        for consumer in app['consumers']:
            try:
                async with session.post(consumer['url'], headers=consumer['headers'], json=params) as response:
                    await handle_client_response(app['db'], response)
            except Exception:
                await insert_failed_message(app['db'], params)

async def produce(app, topic, msg):
    producer = Producer.get_producer(app.loop, app['config'])
    await producer.start()
    try:
        await producer.send_and_wait(topic, str(msg).encode())
    except Exception:
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
            await send(app, params)
    finally:
        await consumer.stop()