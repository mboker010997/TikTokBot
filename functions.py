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


def is_prior_exist(prior, user_id):
    data = select("select * from `surprise` where `prior` = {0}".format(prior,))
    viewed = select("select * from `views` where `user_id` = {0}".format(user_id))
    if len(viewed) != 0:
        viewed = viewed[0]['videos'].split(', ')
    cnt = 0
    for video in data:
        if not str(video['id']) in viewed:
            cnt += 1
    return cnt > 0


def get_random_prior(user_id):
    summa = 0
    mbo = [False] * 11
    for i in range(1, 11):
        if is_prior_exist(i, user_id):
            mbo[i] = True
            summa += i
    num = randint(0, summa - 1)
    for i in range(1, 11):
        if mbo[i]:
            if num - i < 0:
                return i
            num -= i


def get_random_surprise(prior, user_id):
    data = select("select * from `surprise` where `prior` = {0}".format(prior))
    viewed = select("select * from `views` where `user_id` = {0}".format(user_id))
    if len(viewed) != 0:
        viewed = viewed[0]['videos'].split(', ')
    res = []
    for video in data:
        if not str(video['id']) in viewed:
            res.append(video)
    pos = randint(0, len(res) - 1)
    return res[pos]


def get_surprise_by_id(service, id):
    results = service.files().list(pageSize=1000, fields="nextPageToken, files(id, name, mimeType)").execute()['files']
    for data in results:
        if data['name'] == str(id) + '.mp4':
            return data
    return None


def get_id_by_name(name):
    name = name[:-4]
    return int(name)


def add_view(surprise_id, user_id, nickname):
    surprise_id = str(surprise_id)
    viewed = select("select * from `views` where `user_id` = {0}".format(user_id))
    if len(viewed) != 0:
        viewed = viewed[0]['videos'].split(', ')
    length = len(viewed)
    if surprise_id in viewed:
        return
    viewed.append(surprise_id)
    viewed = ', '.join(viewed)
    if length == 0:
        db.cursor.execute("insert into `views` (`user_id`, `nickname`, `videos`) values (?, ?, ?)", (user_id, nickname, viewed,))
    else:
        db.cursor.execute("update `views` set `videos` = ? where `user_id` = ?", (viewed, user_id,))
    db.connection.commit()


def get_name_newfile(dir):
    name = randint(1, 100000000)
    while os.path.exists(dir + str(name)):
        name = randint(1, 100000000)
    return str(name)


def get_new_surprise_id():
    data = select("select * from `surprise` order by `id`")
    return int(data[-1]['name']) + 1


def upload_surprise(service, filename, upload_name):
    file_metadata = {
        'name': upload_name,
        'parents': [folder_id]
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