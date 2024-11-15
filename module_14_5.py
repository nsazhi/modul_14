from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

from crud_functions import *

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.ERROR, filemode='a', filename='./calc_kkal.log', encoding='utf-8',
                    format='%(asctime)s | %(levelname)s | %(message)s')

start_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ],
        [
            KeyboardButton(text='Регистрация'),
            KeyboardButton(text='Купить')
        ]
    ], resize_keyboard=True
)

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
            InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
        ]
    ]
)

product_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Продукт 1', callback_data='product_buying'),
            InlineKeyboardButton(text='Продукт 2', callback_data='product_buying'),
            InlineKeyboardButton(text='Продукт 3', callback_data='product_buying'),
            InlineKeyboardButton(text='Продукт 4', callback_data='product_buying')
        ]
    ]
)


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.', reply_markup=start_menu_kb)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=main_menu_kb)


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    all_products = get_all_products()
    for i in all_products:
        id, title, description, price = i
        await message.answer(f'Название: {title} | Описание: {description} | Цена: {price}')
        with open(f'images/pic{id}.png', "rb") as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=product_kb)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    try:
        await state.update_data(age=int(message.text))
        await message.answer('Введите свой рост:')
        await UserState.growth.set()
    except ValueError:
        logging.error('Некорректное значение возраста')
        await message.answer('Некорректный ответ. Начните еще раз.', reply_markup=main_menu_kb)
        await state.finish()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    try:
        await state.update_data(growth=int(message.text))
        await message.answer('Введите свой вес:')
        await UserState.weight.set()
    except ValueError:
        logging.error('Некорректное значение роста')
        await message.answer('Некорректный ответ. Начните еще раз.', reply_markup=main_menu_kb)
        await state.finish()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    try:
        await state.update_data(weight=int(message.text))
        data = await state.get_data()
        kkal = 10 * data['weight'] + 6.25 * data['growth'] - 5 * data['age'] - 161
        await message.answer(f'Ваша норма в сутки: {int(kkal)} ккал', reply_markup=start_menu_kb)
        await state.finish()
    except ValueError:
        logging.error('Некорректное значение веса')
        await message.answer('Некорректный ответ. Начните еще раз.', reply_markup=main_menu_kb)
        await state.finish()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer('Введите свой возраст:')
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])
    await state.finish()
    await message.answer('Регистрация прошла успешно.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
