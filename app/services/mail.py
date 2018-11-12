import json
import asyncio
import aiosmtplib
from email.mime.text import MIMEText

async def send_notification(app, message):
    auth = None
    if app['config']['email']['auth_required']:
        auth = {
            'username': app['config']['email']['username'],
            'password': app['config']['email']['password']
        }
    kwargs = {
        'loop': app.loop,
        'hostname': app['config']['email']['host'],
        'port': app['config']['email']['port'],
    }

    smtp = aiosmtplib.SMTP(**kwargs)
    
    await smtp.connect()
    if auth:
        await smtp.login(**auth)

    message = MIMEText(json.dumps(message))
    message['From'] = 'carrier@service'
    message['To'] = app['config']['email']['email_to_notify']
    message['Subject'] = 'Problem with Carrier!'

    await smtp.send_message(message)