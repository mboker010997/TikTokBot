from asyncio import sleep
from config import *
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ContentType

likes_bot = Bot(token=config.likes_token)
likes_dp = Dispatcher(likes_bot)
inline_delete = InlineKeyboardButton('Delete', callback_data='delete')
inline_likes_kb = InlineKeyboardMarkup().add(inline_delete)


@likes_dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await sleep(60)
    await message.delete()


@likes_dp.message_handler(content_types=ContentType.ANY)
async def lalala(message: types.Message):
    await message.delete()


@likes_dp.callback_query_handler(lambda c: c.data == 'delete')
async def callback_like(callback_query: types.CallbackQuery):
    await likes_bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()


# def run():
#     # asyncio.set_event_loop(loop)
#     executor.start_polling(likes_dp, skip_updates=True)


if __name__ == '__main__':
    executor.start_polling(likes_dp, skip_updates=True)