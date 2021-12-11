import io
from work import *
from random import randint
import os
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from config import *


def binary_search(arr, x):
    l = -1
    r = len(arr)
    while r - l > 1:
        mid = (l + r) // 2
        if arr[mid] == x:
            return True
        if arr[mid] < x:
            l = mid
        else:
            r = mid
    return False


def get_random_surprise(user_id):
    surprises_quantity = db.cursor.execute("select count(*) from `surprises`").fetchone()[0]
    views_quantity = db.cursor.execute("select count(*) from `views` where `user_id` = ?", (user_id,)).fetchone()[0]
    possible_quantity = surprises_quantity - views_quantity
    if possible_quantity == 0:
        restore_views(user_id)
        views_quantity = db.cursor.execute("select count(*) from `views` where `user_id` = ?", (user_id,)).fetchone()[0]
        possible_quantity = surprises_quantity - views_quantity
    pos = randint(1, possible_quantity)
    it = 1
    surprise = []
    while pos > 0:
        query = "select * from (select `id`, ROW_NUMBER() over (order by `id`) as `row` from `surprises`) where `row` = {0}".format(it)
        surprises = select(query)[0]
        view = db.cursor.execute("select * from `views` where `user_id` = ? and `surprise_id` = ?", (user_id, surprises['id'],)).fetchall()
        if len(view) == 0:
            pos -= 1
            surprise = surprises
        it += 1
    surprise = select("select * from `surprises` where `id` = {0}".format(surprise['id']))[0]
    return surprise


def get_surprise_by_id(service, id):
    results = service.files().list(pageSize=1000, fields="nextPageToken, files(id, name, mimeType)").execute()['files']
    for data in results:
        if data['name'] == str(id) + '.mp4':
            return data
    return None


def get_id_by_name(name):
    name = name[:-4]
    return int(name)


def add_new_row(table_name):
    db.cursor.execute("insert into `?` (`name`) values (?)", (table_name, 'mbo'))
    db.connection.commit()
    return db.cursor.lastrowid


def update_surprise(id, name, file_id):
    db.cursor.execute("update `surprise` set `name` = ?, `file_id` = ? where `id` = ?", (name, file_id, id,))
    db.connection.commit()


def add_view(surprise_id, user_id, username):
    results = select('select * from `views` where `surprise_id` = {0} and `user_id` = {1}'.format(surprise_id, user_id))
    if len(results) != 0:
        return
    db.cursor.execute('insert into `views` (`user_id`, `surprise_id`, `username`) values (?, ?, ?)', (user_id, surprise_id, username))
    db.connection.commit()


def remove_force_surprise(surprise_id):
    db.cursor.execute("delete from `surprises` where `id` = ?", (surprise_id,))
    db.connection.commit()


def restore_views(user_id):
    db.cursor.execute("delete from `views` where `user_id` = ?", (user_id))
    db.connection.commit()


def get_name_newfile(dir):
    name = randint(1, 100000000)
    while os.path.exists(dir + str(name)):
        name = randint(1, 100000000)
    return str(name)


def get_new_surprise_id():
    data = select("select * from `surprises` order by `id` desc limit 1")
    return int(get_id_by_name(data[0]['name'])) + 1


def soft_delete(file):
    if os.path.exists(file):
        os.remove(file)


def upload_surprise(service, filename, upload_name):
    file_metadata = {
        'name': upload_name,
        'parents': [config.folder_id]
    }
    media = MediaFileUpload(filename, mimetype='video/mp4')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')


def download_surprise(service, file_id, filename):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(filename, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()