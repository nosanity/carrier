from aiohttp import web
from app.views import routes
from app.service import consume
from app.utils import get_config, generate_consumers_url
from app import Producer

async def start_background_tasks(app):
    app['kafka_consumer'] = app.loop.create_task(consume(app))

async def cleanup_background_tasks(app):
    app['kafka_consumer'].cancel()
    await app['kafka_consumer']
    await Producer.get_producer().stop()

def init_app(argv=None):
    app = web.Application(middlewares=[
       web.normalize_path_middleware(append_slash=True, merge_slashes=True),
    ])
    
    app['config'] = get_config(argv)

    generate_consumers_url(app)

    app.add_routes(routes) 
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    
    return app

def wsgi(config=None):
    if config:
        argv = [None, '--config', config]
        return init_app(argv)

def run(argv=None):
    app = init_app(argv)
    web.run_app(app, host=app['config']['host'], port=app['config']['port'])