import sys
from db.helpers import DatabaseStartup

if __name__ == '__main__':
    db = DatabaseStartup(sys.argv[1:], force=True)
    db.initialize_db()
    db.close_connection()