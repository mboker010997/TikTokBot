import sqlite3


class SQLiter:

    def __init__(self, f):
        self.connection = sqlite3.connect(f)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.cursor.close()

    def normalize_data(self, data, table_name):
        mbo = self.connection.execute("select * from `{0}`".format(table_name))
        columns = [description[0] for description in mbo.description]
        res = dict()
        for i in range(len(data)):
            res[columns[i]] = data[i]
        return res


    def get_columns(self, table_name):
        mbo = self.connection.execute("select * from `{0}`".format(table_name))
        columns = [description[0] for description in mbo.description]
        return columns

    # def execute(self, command):
    #     with self.connection:
    #         self.cursor.execute(command)