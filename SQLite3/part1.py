import sqlite3

conn = sqlite3.connect('tutorial.db')
c = conn.cursor()

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS mytable(unix REAL, datestamp TEXT, keyword TEXT, value REAL)')

def data_entry():
    c.execute("INSERT INTO mytable VALUES(1451255552, '2016-01-02', 'Python', 8) ")
    conn.commit()   # anytime you modify anything in db
    c.close()
    conn.close()


# create_table()
data_entry()

