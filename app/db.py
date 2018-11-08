from aiomysql import create_pool

async def execute(pool, query, commit=False):
    async with pool.get() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            if commit:
                await conn.commit()
            return cursor

async def all(pool, query):
    cursor = await execute(pool, query)
    return await cursor.fetchall()

async def one(pool, query):
    cursor = await execute(pool, query)
    return await cursor.fetchone()

async def insert(pool, query):
    await execute(pool, query, commit=True)

async def init_db_pool(app):
    config = app['config']
    kwargs = {
        'db': config['mysql']['database'], 
        'host': config['mysql']['host'], 
        'port': config['mysql']['port'],
        'user': config['mysql']['user'], 
        'password': config['mysql']['password'],
        'minsize': config['mysql']['minsize'],
        'maxsize': config['mysql']['maxsize']             
    }
    app['db'] = await create_pool(**kwargs)

async def close_db_pool(app):
    app['db'].close()
    await app['db'].wait_closed()