import mysql.connector

class ConnectionError(Exception):
    pass
class CredentialsError(Exception):
    pass
class SQLError(Exception):
    pass

class UseDatabase:
    def __init__(self, dbconfig):
        self.dbconfig = dbconfig

    def __enter__(self):
        try:
            self.conn = mysql.connector.connect(**self.dbconfig)
            self.cursor = self.conn.cursor()
            return self.cursor
        except mysql.connector.errors.InterfaceError as e:
            raise ConnectionError(e)
        except mysql.connector.errors.ProgrammingError as e:
            raise CredentialsError(e)


    def __exit__(self, exc_type, exc_value, exc_trace):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

        if exc_type is mysql.connector.errors.ProgrammingError:
            raise SQLError(exc_value)
        elif exc_type:
            raise exc_type(exc_value)