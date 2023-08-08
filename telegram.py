import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, state
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import Token, user_id
from main import main, test_parse_channel
import json

bot = Bot(token = Token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
paused = False

class Find(StatesGroup):
    request = State()

class AddGroup(StatesGroup):
    group = State()

def keyboard_menu():
    start_buttons = ['Начать автоматизацию', 'Остановить автоматизацию', 'Ввести запрос', "Добавить группу", "Вывести все запросы"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*start_buttons)
    return keyboard

@dp.message_handler(commands='start')
async def start(message: types.Message):
    id_ = message.from_user.id
    if str(id_) == user_id:
        start_text = 'Здравствуйте! Этот бот предназначен для парсинга телеграмм каналов. \n' \
                     'Чтобы начать работу, нажмите кнопку "Ввести запрос" \n' \
                     'После сохранения запроса, вы можете приступать к старту автоматизации'
        await message.answer(start_text, reply_markup=keyboard_menu())

@dp.message_handler(Text(equals='Ввести запрос'))
async def find1(message: types.Message):
    await message.answer('Введите Ваш запрос: ')
    await Find.next()

@dp.message_handler(state=Find.request)
async def find2(message: types.Message, state: FSMContext):
    request_from_user = message.text

    with open('filter.json', encoding="utf-8") as file:
        filt = json.load(file)
    if request_from_user not in filt["filters"]:
        filt["filters"].append(request_from_user)
        with open('filter.json', 'w', encoding='utf-8') as file:
            json.dump(filt, file, indent=4, ensure_ascii=False)

        await message.answer(f'Ваш запрос {request_from_user} был сохранен!', reply_markup=keyboard_menu())
        await state.finish()
    else:
        await message.answer("Такой запрос уже существует! Введите другой запрос")


@dp.message_handler(Text(equals='Добавить группу'))
async def add_group1(message: types.Message):
    await message.answer('Введите ссылку на группу для сбора данных (без https://): ')
    await AddGroup.next()

@dp.message_handler(state=AddGroup.group)
async def add_group2(message: types.Message, state: FSMContext):
    new_group = message.text

    with open('filter.json', encoding="utf-8") as file:
        filt = json.load(file)

    if new_group not in filt["urls"]:
        filt["urls"].append(new_group)
        with open('filter.json', 'w', encoding='utf-8') as file:
            json.dump(filt, file, indent=4, ensure_ascii=False)

        await message.answer(fr'Группа {new_group} была сохранена!', reply_markup=keyboard_menu())
        await state.finish()
    else:
        await message.answer('Эта группа уже добавлена! Введите ссылку на другую группу')


@dp.message_handler(Text(equals='Вывести все запросы'))
async def all_finds(message: types.Message):

    with open('filter.json', encoding="utf-8") as file:
        filt = json.load(file)

    new_filt_list = filt["filters"]
    numbered_list = '\n'.join([f"{i + 1}. {item}" for i, item in enumerate(new_filt_list)])

    await message.answer(f'Все сохраненные запросы, по которым осуществляется поиск: \n{numbered_list}')

@dp.message_handler(Text(equals="Остановить автоматизацию"))
async def stop(message: types.Message):
    global paused
    paused = True
    await message.answer("Бот остановлен")
    return paused

@dp.message_handler(Text(equals='Начать автоматизацию'))
async def message_every_minute(message: types.Message):
    await message.answer('Автоматизация начата. Пожалуйста, подождите! Процесс может занять время')
    with open("filter.json", "r") as file:
        filters = json.load(file)["filters"]
    global paused
    paused = False
    while not paused:
        await main()
        for filt in filters:
            f = open(f'{filt}.xlsx', 'rb')
            await bot.send_document(message.chat.id, f)
        await asyncio.sleep(300)

if __name__ == '__main__':
    executor.start_polling(dp)