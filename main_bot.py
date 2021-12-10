from google.oauth2 import service_account
from googleapiclient.discovery import build
from functions import *
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType
import likes
import tiktok


# Debug beg --------------------------------------------------------------------------------------------------------
# config.debug()
# Debug end --------------------------------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.token)
dp = Dispatcher(bot)

credentials = service_account.Credentials.from_service_account_file(
        config.SERVICE_ACCOUNT_FILE, scopes=config.SCOPES)
service = build('drive', 'v3', credentials=credentials)

inline_next = InlineKeyboardButton('Next', callback_data='next')
inline_like = InlineKeyboardButton('Like', callback_data='like')
inline_delete = InlineKeyboardButton('Delete', callback_data='delete')
inline_video_kb = InlineKeyboardMarkup().row(inline_like, inline_delete)
inline_video_kb.add(inline_next)

inline_accept = InlineKeyboardButton('Accept', callback_data='accept')
inline_decline = InlineKeyboardButton('Decline', callback_data='decline')
inline_suggest_kb = InlineKeyboardMarkup().add(inline_accept)
inline_suggest_kb.add(inline_decline)

inline_reset = InlineKeyboardButton('Reset', callback_data='reset')
inline_reset_kb = InlineKeyboardMarkup().add(inline_reset)

surprise_count = get_new_surprise_id()


async def send_random_surprise(user):
    surprise = get_random_surprise(user.id)
    filename = 'temp/' + get_name_newfile('temp/') + '.mp4'
    download_surprise(service, surprise['file_id'], filename)
    add_view(surprise['id'], user.id, user.full_name)
    with open(filename, 'rb') as video:
        await bot.send_video(user.id, video, caption=str(get_id_by_name(surprise['name'])), reply_markup=inline_video_kb)
    os.remove(filename)


@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    res = '<b><i>Добро пожаловать в ТикТок Премиум!</i></b>\nЗдесь ты можешь насладиться дрочибельным контентом из ТикТока.\n' \
          'Если введешь число, то получишь видос с таким id.'
    await message.answer(res, parse_mode='html')
    await send_random_surprise(message.from_user)


@dp.message_handler(commands=['remove_force'])
async def remove_force(message: types.Message):
    await message.delete()
    if message.from_user.id != 568426183:
        return
    text = message.text
    words = text.split()
    words = words[1:]
    if len(words) == 1:
        id = words[0]
        if id.isdigit():
            id = int(id)
            surprise = get_surprise_by_id(id)
            if surprise:
                await bot.send_message(568426183, 'Удалён видос ' + str(id) + '!')
                service.files().delete(fileId=surprise['file_id']).execute()
                remove_force_surprise(surprise['id'])


@dp.message_handler(content_types=ContentType.ANY)
async def lalala(message: types.Message):
    text = message.text
    await message.delete()
    temp_filename = 'temp/' + get_name_newfile('temp/') + '.mp4'
    if text[0:4] == "http":
        iter = 0
        while not tiktok.download_tiktok(text, temp_filename):
            with open(temp_filename, 'rb') as video:
                last_id = add_new_row('surprises')
                new_name = str(last_id)
                upload_name = new_name + '.mp4'
                file_id = upload_surprise(service, temp_filename, upload_name)
                soft_delete(temp_filename)
                # update_surprise(last_id, upload_name, file_id)
                await bot.send_message(568426183, 'Добавлен видос ' + new_name)
            iter += 1
            if iter > 20:
                await bot.send_message(568426183, "Не удалось загрузить видос по ссылке(")
                break
    else:
        if message.content_type != 'text':
            return
        if text.isdigit():
            id = int(text)
            surprise = get_surprise_by_id(id)
            if not surprise:
                await send_random_surprise(message.from_user)
            else:
                filename = 'temp/' + get_name_newfile('temp/') + '.mp4'
                download_surprise(service, surprise['file_id'], filename)
                with open(filename, 'rb') as video:
                    await bot.send_video(message.from_user.id, video, caption=str(get_id_by_name(surprise['name'])), reply_markup=inline_video_kb)
                    add_view(surprise['id'], message.from_user.id, message.from_user.full_name)
                soft_delete(filename)
        else:
            await send_random_surprise(message.from_user)


@dp.callback_query_handler(lambda c: c.data == 'next')
async def callback_next(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await send_random_surprise(callback_query.from_user)


@dp.callback_query_handler(lambda c: c.data == 'like')
async def callback_like(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    id = callback_query.message.caption
    surprise = get_surprise_by_id(id)
    filename = 'temp/' + get_name_newfile('temp/') + '.mp4'
    download_surprise(service, surprise['file_id'], filename)
    with open(filename, 'rb') as video:
        try:
            await likes.likes_bot.send_video(callback_query.from_user.id, video, caption=id, reply_markup=likes.inline_likes_kb)
        except Exception as e:
            await bot.send_message(callback_query.from_user.id, "Запустите бота @likes_inforesult_bot!")
    soft_delete(filename)


@dp.callback_query_handler(lambda c: c.data == 'delete')
async def callback_delete(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'accept')
async def callback_accept(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    temp_filename = callback_query.message.caption.split(' ')[-1]
    last_id = add_new_row('surprises')
    new_name = str(last_id)
    upload_name = new_name + '.mp4'
    file_id = upload_surprise(service, temp_filename, upload_name)
    soft_delete(temp_filename)
    # update_surprise(last_id, upload_name, file_id)
    await bot.send_message(568426183, 'Добавлен видос ' + new_name)
    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'decline')
async def callback_prior_choice(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    temp_filename = callback_query.message.caption.split(' ')[-1]
    soft_delete(temp_filename)
    await callback_query.message.delete()


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.create_task(run())
    # executor.start_polling(dp, skip_updates=True, loop=loop)
    executor.start_polling(dp, skip_updates=True)
