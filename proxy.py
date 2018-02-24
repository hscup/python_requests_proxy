import mysql.connector
from mysql.connector import errorcode
from datetime import date, datetime, timedelta


class Proxy:
    def __init__(self, username, password, host, database, proxy_table):
        self.username = username
        self.password = password
        self.host = host
        self.database = database
        self.proxy_table = proxy_table
        self.connection = mysql.connector.connection.MySQLConnection()

    def connect_to_db(self):
        try:
            if not self.connection.is_connected():
                self.connection = mysql.connector.connect(user=self.username, password=self.password,
                                                          host=self.host,
                                                          database=self.database)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def close_db_connection(self):
        if self.connection.is_connected():
            self.connection.close()

    def query_random_proxy(self, query=None, params=None):
        result = []
        self.connect_to_db()
        if not self.connection.is_connected():
            print("Can not connect to database")
            return
        cursor = self.connection.cursor()
        if not query:
            query = "SELECT ip, port FROM {} ORDER BY RAND() LIMIT 1".format(self.proxy_table)
        cursor.execute(query, params)
        for (ip, port) in cursor:
            result.append("{}:{}".format(ip, port))
        cursor.close()
        self.close_db_connection()
        return result


if __name__ == "__main__":
    proxy = Proxy('root', 'secret', '127.0.0.1', 'testdb', 'proxies')
    hire_start = date(1999, 1, 1)
    hire_end = date(2025, 12, 31)
    result = proxy.query_random_proxy()
    for (ip, port) in result:
        print("{}:{}".format(ip, port))
