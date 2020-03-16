import sqlite3
import time
import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style
style.use('fivethirtyeight')


conn = sqlite3.connect('tutorial.db')
c = conn.cursor()

def create_table():
    c.execute('CREATE TABLE IF NOT EXISTS mytable(unix REAL, datestamp TEXT, keyword TEXT, value REAL)')

def data_entry():
    c.execute("INSERT INTO mytable VALUES(1451255552, '2016-01-02', 'Python', 8) ")
    conn.commit()   # anytime you modify anything in db
    c.close()
    conn.close()

def dynamic_data_entry():
    unix = time.time()
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S'))
    keyword = 'Python'
    value = random.randrange(0,10)
    c.execute("INSERT INTO mytable (unix, datestamp, keyword, value) VALUES (?, ?, ?, ?)",
              (unix, date, keyword, value))
    conn.commit()

def read_from_db():
    # c.execute("SELECT * FROM mytable WHERE value>3 AND keyword='Python'")
    c.execute("SELECT keyword, unix FROM mytable WHERE unix > 1452618731")
    # data = c.fetchall()
    # print(data)
    for row in c.fetchall():            # iterate through the rows
        print(row)                      # each row is printed as a tuple

def graph_data():
    c.execute('SELECT unix, value FROM mytable')
    dates=[]
    values=[]
    for row in c.fetchall():
        # print(row[0])
        # print(datetime.datetime.fromtimestamp(row[0]))
        dates.append(datetime.datetime.fromtimestamp(row[0]))
        values.append(row[1])
    plt.plot_date(dates, values, '-')
    plt.show()


# create_table()
# data_entry()
# for i in range(10):
#     dynamic_data_entry()
#     time.sleep(1)

# read_from_db()

graph_data()

c.close()
conn.close()

