import json
import base64
import asyncio
from datetime import datetime, timedelta
from app.services import kafka
from app.services.db import all, insert, update
from app.services.mail import send_notification

async def handle_failed_message(pool, msg, consumer, resend=0):
    if resend == 0:
        await insert_failed_message(pool, msg, consumer)
    else:
        await update_failed_message(pool, msg, consumer, resend)

async def handle_failed_messages_by_schedule(app):
    while True:
        messages = await fetch_failed_messages(app['db'])

        for message in messages:
            if message['attempts_to_resend'] >= 5:
                await send_notification(app, message)
                await set_undelivered(app['db'], message)
                continue
            elif 0 <= message['attempts_to_resend'] < 2:
                delta_in_sec = 30
            elif 2 <= message['attempts_to_resend'] <= 3:
                delta_in_sec = 180
            elif message['attempts_to_resend'] == 4:
                delta_in_sec = 300

            updated_at = datetime.strptime(message['updated_at'], "%Y-%m-%d %H:%M:%S")

            if abs((updated_at - datetime.utcnow()).total_seconds()) > delta_in_sec:
                params = {
                    'topic': message['topic'],
                    'partition': message['partition'],
                    'offset': message['offset'],
                    'key': message['key'], 
                    'value': message['value'],
                    'timestamp': message['timestamp']
                }
                resend = message['attempts_to_resend'] + 1
                consumer = {
                    'url': message['consumer_url'],
                    'headers': json.loads(message['consumer_headers'])
                }
                result = await kafka.send_to_consumer(app, consumer, params, resend)
                if result:
                    await delete_entry(app['db'], message)

        await asyncio.sleep(app['config']['period_to_resend']) 

async def fetch_failed_messages(pool):
    messages = []
    for msg in await all(pool, "SELECT * FROM message_failed_to_send WHERE undelivered = 0;"):
        messages.append({
            'id': msg[0],
            'topic': msg[1],
            'partition': msg[2],
            'offset': msg[3],
            'value': base64.b64decode(msg[4]).decode("utf-8"),
            'key': msg[5],
            'timestamp': msg[6],
            'consumer_url': msg[7],
            'consumer_headers': base64.b64decode(msg[8]).decode("utf-8"),
            'attempts_to_resend': msg[9],
            'undelivered': msg[10],
            'created_at': str(msg[11]),
            'updated_at': str(msg[12])
        })  

    return messages

async def delete_entry(pool, msg):
    query = "DELETE FROM message_failed_to_send WHERE id = {}".format(msg['id'])
    await update(pool, query)

async def set_undelivered(pool, msg):
    query = """ UPDATE 
                    message_failed_to_send 
                SET 
                    undelivered = 1,
                    updated_at = NOW()
                WHERE 
                    id = {}
            """.format(
                msg['id']
            )
    await update(pool, query)

async def update_failed_message(pool, msg, consumer, resend):
    query = """ UPDATE 
                    message_failed_to_send 
                SET 
                    attempts_to_resend = {},
                    updated_at = NOW()
                WHERE 
                    consumer_url = '{}'
                    AND
                    _topic = '{}'
                    AND 
                    _offset = {} 
            """.format(
                resend, 
                consumer['url'],
                msg['topic'], 
                msg['offset']
            )
            
    await update(pool, query)

async def insert_failed_message(pool, msg, consumer):
    headers = json.dumps(consumer['headers'])
    query = [
        "INSERT INTO message_failed_to_send VALUES (NULL, ",
        "'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}'".format(
            msg['topic'], 
            msg['partition'],
            msg['offset'],
            base64.b64encode(msg['value'].encode()).decode("utf-8"),
            msg['key'],
            msg['timestamp'],
            consumer['url'],
            base64.b64encode(headers.encode()).decode("utf-8")
        ),
        ", DEFAULT, DEFAULT, NOW(), NOW());"
    ]
    await insert(pool, "".join(query))