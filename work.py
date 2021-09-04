from sqliter import SQLiter

db = SQLiter('db.db')


def get_table(table):
    info = db.cursor.execute('SELECT * FROM `?`', (table,)).fetchall()
    res = []
    for row in info:
        res.append(db.normalize_data(row, table))
    return res


def select(command):
    data = db.cursor.execute(command).fetchall()
    mbo = db.connection.execute(command)
    columns = [description[0] for description in mbo.description]
    res = []
    for row in data:
        add_row = dict()
        for i in range(len(row)):
            add_row[columns[i]] = row[i]
        res.append(add_row)
    return res