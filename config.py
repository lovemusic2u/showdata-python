import pymysql

def get_connection():
    con = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database=''
    )
    return con
