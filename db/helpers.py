import sys
import asyncio
import aiomysql

from pymysql.err import OperationalError
from app.utils import BASE_DIR, get_config

class DatabaseStartup():

    async def initialize_connection(self):
        try:
            self._connection = await aiomysql.connect(**self._clean_db)
        except OperationalError:
            self._connection = await aiomysql.connect(**self._exists_db)
            self._is_new = False

    def close_connection(self):
        self._connection.close()

    def __init__(self, config_name, force=False):
        self._force = force
        self._loop = asyncio.get_event_loop()
        self._config = get_config(config_name)
        self._clean_db = {
            'host': self._config['mysql']['host'],
            'user': 'root',
            'port': self._config['mysql']['port'],
            'loop': self._loop              
        }
        self._exists_db = {
            'host': self._config['mysql']['host'], 
            'user': self._config['mysql']['user'], 
            'password': self._config['mysql']['password'], 
            'port': self._config['mysql']['port'], 
            'loop': self._loop            
        }
        self._is_new = True

    def initialize_db(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.do_tasks())

    async def do_tasks(self):
        await self.initialize_connection()
        if self._is_new:
            await self.set_credentials()
            await self.create_table()
        elif not self._is_new and self._force:
            await self.create_table()
        
    async def set_credentials(self):
        async with self._connection.cursor() as cursor:
            if self._config['mysql']['user'] == 'root':
                query = "ALTER USER 'root' IDENTIFIED BY '{}';".format(self._config['mysql']['password'])
            else:
                queries = [
                    "CREATE USER IF NOT EXISTS '{}'@'%' IDENTIFIED BY '{}';".format(
                        self._config['mysql']['user'],
                        self._config['mysql']['password']
                    ),
                    "ALTER USER 'root' IDENTIFIED BY '{}';".format(self._config['mysql']['password'])
                ]  
                query = "".join(queries)
            await cursor.execute(query)
            await self._connection.commit()

    async def create_table(self):
        async with self._connection.cursor() as cursor:
            query = self.get_table_query(self._config['mysql']['user'])
            await cursor.execute(query)
            await self._connection.commit()

    def get_table_query(self, user):
        return """
            DROP DATABASE IF EXISTS carrier;
            CREATE DATABASE carrier CHARACTER SET utf8mb4;
            USE carrier;
            GRANT ALL PRIVILEGES ON carrier.* TO {}; 
            CREATE TABLE message_failed_to_send (
                id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                _topic VARCHAR(256) NOT NULL,
                _partition VARCHAR(256) NOT NULL,
                _offset VARCHAR(256) NOT NULL,
                _value VARCHAR(1024) NOT NULL,
                _key VARCHAR(265),
                _timestamp VARCHAR(20) NOT NULL,
                consumer_url VARCHAR(512) NOT NULL,
                consumer_headers VARCHAR(512) NOT NULL,
                attempts_to_resend INT DEFAULT 0 NOT NULL,
                undelivered TINYINT DEFAULT 0 NOT NULL,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW() NOT NULL
            );
        """.format(user)