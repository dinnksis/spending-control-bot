from aiogram import Router, Dispatcher
import bcrypt
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import database_safety
from database_safety import user_adding, is_user_registered
from contextlib import closing

login=''
flag=0

router = Router()

# Клавиатура
main_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='регистрация'), KeyboardButton(text='вход')],
    ],
    resize_keyboard=True
)


# состояния FSM
class Form(StatesGroup):
    waiting_for_registration_login = State()
    waiting_for_registration_password = State()
    waiting_for_vhod_login = State()
    waiting_for_vhod_password = State()
    authorizedd = State()


# Обработчик команды /start
@router.message(lambda message: message.text.lower() == '/start')
async def send_welcome(message: Message):
    await message.answer('вы запустили telegram-бота для управления расходами. надеюсь, вам понравится:). пожалуйства, войдите в систему или зарегестрируйтесь',
                         reply_markup=main_buttons)


#рeгистрация
@router.message(lambda message: message.text and message.text.lower() == 'регистрация')
async def waiting_registration_login(message: Message,state: FSMContext):
    await message.answer('придумайте логин')
    await state.set_state(Form.waiting_for_registration_login)


#ожидание ввода логина
@router.message(Form.waiting_for_registration_login)
async def waiting_registration_password(message: Message, state: FSMContext):
    login=message.text.strip()
    if (database_safety.is_user_registered(login)):
        await message.reply("такой логин уже занят(. попробуйте придумать другой:")
        return #вернуться если логин занят
    else: #если логин свободен
        await state.update_data(login=login)  # сохраняем логин в состоянии
        await message.answer("придумайте пароль:")
        await state.set_state(Form.waiting_for_registration_password)  # переводит в состотяние ожидания пароля


# Ожидание ввода пароля
@router.message(Form.waiting_for_registration_password)
async def take_registration_password(message: Message, state: FSMContext):
    password = message.text.strip()

    # Получаем логин из состояния
    data = await state.get_data()
    login = data['login']

    # Сохранение в базу данных
    user_adding(login, password)
    await message.answer("вы успешно зарегистрированы!")
    #надо открыть меню основное наше ему
    await state.clear()
    global authorized
    authorized=True
    #await state.set_state(Form.authorizedd)
    #await state.authorized.set() #установка того, что чел зашел в систему


#вход
@router.message(lambda message: message.text and message.text.lower() == 'вход')
async def waiting_vhod_login(message: Message, state: FSMContext):
    await message.answer('введите логин')
    await state.set_state(Form.waiting_for_vhod_login)


#ожидание ввода логина
@router.message(Form.waiting_for_vhod_login)
async def waiting_vhod_password(message: Message, state: FSMContext):
    login = message.text.strip()
    if not(database_safety.is_user_registered(login)):
        await message.reply("кажется,такого логина не существует,попробуйте еще раз:")
        return  # вернуться если логин занят
        # по возможности должны вылезти кнопки зарегесрироватся и попробывать еще раз
    else:
        await state.update_data(login=login)
        await message.answer("введите пароль:")
        await state.set_state(Form.waiting_for_vhod_password) # переводит в состотяние ожидания пароля


# Ожидание ввода пароля
@router.message(Form.waiting_for_vhod_password)
async def take_vhod_password(message: Message, state: FSMContext):
    password = message.text.strip()

    # Получаем логин из состояния
    data = await state.get_data()
    global login
    login = data.get("login")
    if database_safety.check_password(login,password):
        #сделать чтобы попадал в основную систему
        #await message.answer("вы вошли в систему!")
        global flag
        flag = 1
        await state.clear()

        #await state.set_state(Form.authorizedd)# установка того, что чел зашел в систему
    else:
        await message.answer("неправильный пароль, попробуйте еще раз")
        return



def authorized():
    if flag==1:
        return True
    return False
def login():
    return login

# регистрация всех обработчиков в диспетчере
def register_handlers(dp: Dispatcher):
    dp.include_router(router)
