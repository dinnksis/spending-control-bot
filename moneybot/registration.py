from aiogram import Router, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database_safety import add_user_to_database, is_user_registered, check_password
from handlers import buttons
import global_values as gv

router = Router()

# изначальная клавиатура
main_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='регистрация'), KeyboardButton(text='вход')],
    ],
    resize_keyboard=True
)


# состояния FSM
class Form(StatesGroup):
    waiting_for_registration_login_state = State()
    waiting_for_registration_password_state = State()
    waiting_for_login_login_state = State()
    waiting_for_login_password_state = State()
    authorized_state = State()


# обработчик команды /start
@router.message(lambda message: message.text and message.text.lower() == '/start')
async def send_welcome(message: Message):
    gv.login[message.from_user.id] = ''
    gv.is_authorized[message.from_user.id] = False
    await message.answer('вы запустили telegram-бота для управления расходами. надеюсь, вам понравится:). '
                         'пожалуйства, войдите в систему или зарегистрируйтесь',
                         reply_markup=main_buttons)


# рeгистрация
@router.message(lambda message: message.text and message.text.lower() == 'регистрация')
async def wait_for_registration_login(message: Message, state: FSMContext):
    await message.answer('придумайте логин:')
    await state.set_state(Form.waiting_for_registration_login_state)


# ожидание ввода логина
@router.message(Form.waiting_for_registration_login_state)
async def wait_for_registration_password(message: Message, state: FSMContext):
    gv.login[message.from_user.id] = message.text.strip().lower()
    if is_user_registered(gv.login[message.from_user.id]):
        await message.reply('такой логин уже занят:(. попробуйте придумать другой:')
        return
        # вернуться, если логин занят
    # если логин свободен
    await state.update_data(login=gv.login[message.from_user.id])  # сохраняем логин в состоянии
    await message.answer('придумайте пароль:')
    await state.set_state(Form.waiting_for_registration_password_state)  # переводит в состояние ожидания пароля


# ожидание ввода пароля
@router.message(Form.waiting_for_registration_password_state)
async def take_registration_password(message: Message, state: FSMContext):
    password = message.text.strip()

    # получаем логин из состояния
    data = await state.get_data()
    gv.login[message.from_user.id] = data['login'].lower()

    # сохранение в базу данных
    add_user_to_database(gv.login[message.from_user.id], password)
    await state.clear()
    gv.is_authorized[message.from_user.id] = True

    # вход в основную систему
    await message.reply('вы успешно зарегистрировались!', reply_markup=buttons)


# вход
@router.message(lambda message: message.text and message.text.lower() == 'вход')
async def wait_for_login_login(message: Message, state: FSMContext):
    await message.answer('введите логин:')
    await state.set_state(Form.waiting_for_login_login_state)


# ожидание ввода логина
@router.message(Form.waiting_for_login_login_state)
async def wait_for_login_password(message: Message, state: FSMContext):
    gv.login[message.from_user.id] = message.text.strip().lower()
    if not(is_user_registered(gv.login[message.from_user.id])):
        await message.reply('кажется,такого логина не существует, попробуйте еще раз:')
        return  # вернуться, если логин занят
    else:
        await state.update_data(login=gv.login[message.from_user.id])
        await message.answer('введите пароль:')
        await state.set_state(Form.waiting_for_login_password_state)
        # переводит в состояние ожидания пароля


# ожидание ввода пароля
@router.message(Form.waiting_for_login_password_state)
async def take_login_password(message: Message, state: FSMContext):
    password = message.text.strip()

    # получаем логин из состояния
    data = await state.get_data()
    login = data.get('login').lower()
    if check_password(login, password):
        # попадание в основную систему
        gv.is_authorized[message.from_user.id] = True
        gv.login[message.from_user.id] = login
        await state.clear()
        await message.reply('вы успешно вошли в систему!', reply_markup=buttons)
    else:
        await message.answer('неправильный пароль, попробуйте еще раз')
        return


# регистрация всех обработчиков в диспетчере
def register_handlers(dp: Dispatcher):
    dp.include_router(router)
