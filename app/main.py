import os
from aiohttp import web
from app import Producer
from app.views import routes
from app.services.kafka import consume
from app.services.failed_messages import handle_failed_messages_by_schedule
from app.services.db import init_db_pool, close_db_pool
from app.utils import get_config, generate_consumers_url
from db.helpers import DatabaseStartup
import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

async def start_background_tasks(app):
    app['kafka_consumer'] = app.loop.create_task(consume(app))
    app.loop.create_task(handle_failed_messages_by_schedule(app))

async def cleanup_background_tasks(app):
    app['kafka_consumer'].cancel()
    await app['kafka_consumer']

def init_sentry(app):
    sentry_sdk.init(
        dsn=app['config']['sentry_dsn'],
        integrations=[AioHttpIntegration()],
        environment='carrier'
    )


def init_app(argv=None):
    app = web.Application(middlewares=[
       web.normalize_path_middleware(append_slash=True, merge_slashes=True),
    ])
    
    app['config'] = get_config(argv)

    generate_consumers_url(app)

    app.add_routes(routes) 

    app.on_startup.append(init_db_pool)
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(close_db_pool)
    app.on_cleanup.append(cleanup_background_tasks)

    return app

def container():
    config = os.environ.get('CONFIG', None)
    force_db_init = os.environ.get('FORCE_DB_INIT', None)
    if config:
        argv = [None, '--config', config]
        db = DatabaseStartup(argv, force_db_init)
        db.initialize_db()
        db.close_connection()
        return init_app(argv)

def wsgi(config=None):
    if config:
        argv = [None, '--config', config]
        return init_app(argv)

def run(argv=None):
    app = init_app(argv)
    init_sentry(app)
    web.run_app(app, host=app['config']['host'], port=app['config']['port'])