import sqlite3

def create_db():
    with open('tgbot/database/create_tables.sql') as f:
        sql = f.read()
    with sqlite3.connect('test.db') as con:
        cur = con.cursor()
        cur.executescript(sql)

if __name__ == '__main__':
    create_db()