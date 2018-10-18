from aiohttp import web
from app.views import routes
from app.service import consume

async def start_background_tasks(app):
    app['kafka_consumer'] = app.loop.create_task(consume(app))

async def cleanup_background_tasks(app):
    app['kafka_consumer'].cancel()
    await app['kafka_consumer']

def run(argv=None):
    app = web.Application()
    app.add_routes(routes) 
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    web.run_app(app)