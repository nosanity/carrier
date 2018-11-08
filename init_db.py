import sys
import asyncio
import aiomysql

from app.utils import BASE_DIR, get_config

def get_commands(user):
    return [
        "DROP DATABASE IF EXISTS carrier;",
        "CREATE DATABASE carrier CHARACTER SET utf8mb4;",
        "USE carrier;",
        "GRANT ALL PRIVILEGES ON carrier.* TO {};".format(user), 
        "CREATE TABLE message_failed_to_send (" \
            "id INT NOT NULL PRIMARY KEY AUTO_INCREMENT," \
            "_topic VARCHAR(256) NOT NULL," \
            "_partition VARCHAR(256) NOT NULL," \
            "_offset VARCHAR(256) NOT NULL," \
            "_value VARCHAR(1024) NOT NULL," \
            "_key VARCHAR(265)," \
            "_timestamp VARCHAR(20) NOT NULL," \
            "attempts_to_resend INT DEFAULT 0 NOT NULL," \
            "created_at TIMESTAMP NOT NULL," \
            "updated_at TIMESTAMP NOT NULL" \
        ");"
    ]

async def create_db(commands, config, loop):
    pool = await aiomysql.create_pool(
        user=config['mysql']['user'], 
        password=config['mysql']['password'], 
        host=config['mysql']['host'], 
        port=config['mysql']['port'], 
        loop=loop
    )
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("".join(commands))
            await conn.commit()

    pool.close()
    await pool.wait_closed()

config = get_config(sys.argv[1:])

commands = get_commands(config['mysql']['user'])

loop = asyncio.get_event_loop()
loop.run_until_complete(create_db(commands, config, loop))