from aiogram import Router, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import add_expense, add_goal, get_expenses, get_goals, delete_all_data
from datetime import datetime
import registration
import global_values as gv

router = Router()
# объект, который будет исп. для регистрации обработчиков команд и сообщений

# форматирование чисел для упрощения чтения


def format_number_with_dots(number_str: str) -> str:
    parts = number_str.split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else ''
    reversed_integer = integer_part[::-1]
    formatted_reversed_integer = '.'.join(reversed_integer[i:i + 3] for i in range(0, len(reversed_integer), 3))
    formatted_integer = formatted_reversed_integer[::-1]
    if decimal_part:
        return f"{formatted_integer},{decimal_part}"
    else:
        return formatted_integer


# состояния FSM
class Form(StatesGroup):
    waiting_for_expense_amount = State()
    waiting_for_expense_category = State()
    waiting_for_goal_category = State()
    waiting_for_goal_amount = State()


# клавиатура
buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='добавить трату'), KeyboardButton(text='установить лимит')],
        [KeyboardButton(text='статистика расходов'), KeyboardButton(text='лимиты')],
        [KeyboardButton(text='помощь'), KeyboardButton(text='удалить данные')],
        [KeyboardButton(text='выйти из аккаунта')]
    ],
    resize_keyboard=True
)


# обработчики
# выход из акка
@router.message(lambda message: message.text.lower() == 'выйти из аккаунта')
async def goodbye(message: Message):
    gv.login = ''
    gv.is_authorized = False
    await message.answer('вы вышли из системы. пожалуйства, войдите в систему или зарегистрируйтесь',
                         reply_markup=registration.main_buttons)


# обработчик команды /help и помощь, если чел зареган
@router.message(lambda message: (message.text.lower() == '/help' or message.text == 'помощь') and gv.is_authorized)
async def send_help(message: Message):
    await message.reply('''вы запустили бота счетчика расходов. возможные действия:

добавить трату - добавление потраченной суммы

установить лимит - установка суммы, которую вы готовы потратить на данную категорию

статистика расходов - ваши расходы по всем добавленным категориям и выполнение целей

лимиты - список установленных ограничений и то, выполнены ли они на данный момент

удалить данные - удаление всех целей и расходов данного аккаунта''', reply_markup=buttons)


# обработчик команды /help и помощь, если чел не зареган
@router.message(lambda message: (message.text.lower() == '/help' or message.text == 'помощь'))
async def send_help(message: Message):
    await message.reply('''вы запустили бота счетчика расходов. возможные действия:

добавить трату - добавление потраченной суммы

установить лимит - установка суммы, которую вы готовы потратить на данную категорию

статистика расходов - ваши расходы по всем добавленным категориям и выполнение целей

лимиты - список установленных ограничений и то, выполнены ли они на данный момент

удалить данные - удаление всех целей и расходов данного аккаунта

но сначала вам надо зарегистрироваться или войти в аккаунт, до этого кнопки работать не будут :<''')


# обработчик всех сообщений если чел не авторизирован
@router.message(lambda _: not gv.is_authorized)
async def not_authorized(message: Message):
    await message.reply('пожалуйста, сначала войдите в аккаунт или зарегистрируйтесь!')


# обработчик команды добавления траты
@router.message(lambda message: (message.text.lower() == 'добавить трату'))
async def add_expense_handler(message: Message, state: FSMContext):
    await message.answer('введите сумму расходов:')
    # просит у пользователя сумму и переводит в состояние ожидания суммы
    await state.set_state(Form.waiting_for_expense_amount)


# ожидание ввода суммы расходов
@router.message(Form.waiting_for_expense_amount)
async def process_expense_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
        await state.update_data(expense_amount=amount)
        await message.answer('введите категорию расходов:')
        await state.set_state(Form.waiting_for_expense_category) # переводит в состотяние ожидания категории расхода
    except ValueError:
        await message.reply('пожалуйста, введите корректную положительную сумму.')


# ожидание ввода категории расходов
@router.message(Form.waiting_for_expense_category)
async def process_expense_category(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data['expense_amount']
    category = message.text.strip()
    date = datetime.now().strftime('%Y-%m-%d')

    # сохранение в базу данных
    add_expense(gv.login, amount, category.lower(), date)

    await message.answer('трата добавлена!')
    await state.clear()


# обработчик команды /setgoal и добавления цели
@router.message(lambda message: message.text.lower() == 'установить лимит')
async def start_setting_goal(message: Message, state: FSMContext):
    await message.answer('введите категорию лимита:')
    await state.set_state(Form.waiting_for_goal_category)


# ожидание ввода категории цели
@router.message(Form.waiting_for_goal_category)
async def process_goal_category(message: Message, state: FSMContext):
    category = message.text.strip()
    await state.update_data(goal_category=category)
    await message.answer('введите сумму лимита:')
    await state.set_state(Form.waiting_for_goal_amount)


# ожидание ввода суммы цели
@router.message(Form.waiting_for_goal_amount)
async def process_goal_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
        data = await state.get_data()
        category = data['goal_category']
        date = datetime.now().strftime('%Y-%m-%d')

        # сохранение в базу данных
        result_message = add_goal(gv.login, category.lower(), amount, date)

        await message.answer(result_message)
        await state.clear()
    except ValueError:
        await message.reply('пожалуйста, введите корректную положительную сумму.')


# обработчик команды удаления всех данных
@router.message(lambda message: message.text.lower() == 'удалить данные')
async def delete_all_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='да', callback_data='confirm_delete'),
                InlineKeyboardButton(text='нет', callback_data='cancel_delete')
            ]
        ]
    )
    await message.reply("вы уверены, что хотите удалить все данные?", reply_markup=keyboard)


# обработчик подтверждения удаления данных
@router.callback_query(lambda c: c.data == 'confirm_delete')
async def confirm_delete_callback(callback_query: CallbackQuery):
    delete_all_data(gv.login)
    await callback_query.message.edit_text('ваши данные успешно удалены.')
    await callback_query.answer()


# обработчик отмены удаления данных
@router.callback_query(lambda c: c.data == 'cancel_delete')
async def cancel_delete_callback(callback_query: CallbackQuery):
    await callback_query.message.edit_text('удаление данных отменено.')
    await callback_query.answer()


# обработчик команды вывода статистики расходов
@router.message(lambda message: message.text.lower() == 'статистика расходов')
async def report_handler(message: Message):
    expenses = get_expenses(gv.login)
    goals = get_goals(gv.login)
    if not expenses:
        await message.reply('у вас нет расходов.')
        return
    report = 'ваши расходы:\n\n'
    datee = dict()
    dateg = dict()
    if goals:
        for category, amount in goals:
            dateg[category] = float(amount)
    for amount, category, date in expenses:
        if category in datee:
            datee[category] += float(amount)
        else:
            datee[category] = float(amount)
    for key, value in datee.items():
        report += f'{key} - {format_number_with_dots(str(value))} рублей\n'
        if key in dateg:
            difference = value - dateg[key]
            if difference > 0:
                report += f'цель {format_number_with_dots(str(dateg[key]))} рублей не выполнена. ' \
                          f'лимит превышен на {format_number_with_dots(str(difference))} рублей\n'
            else:
                report += f'цель {format_number_with_dots(str(dateg[key]))} рублей выполнена. ' \
                          f'до превышения лимита {format_number_with_dots(str(abs(difference)))} рублей\n'
        else:
            report += f'лимит для категории отсутствует\n'
        report += '\n'
    await message.reply(report)


# обработчик команды /listgoals и вывода списка целей
@router.message(lambda message: message.text.lower() == 'лимиты')
async def listgoals_handler(message: Message):
    goals = get_goals(gv.login)
    expenses = get_expenses(gv.login)
    if not goals:
        await message.reply('у вас нет установленных лимитов')
        return
    report = 'ваши лимиты:\n\n'
    exp = dict()
    if expenses:
        for amount, category, date in expenses:
            if category in exp:
                exp[category] += float(amount)
            else:
                exp[category] = float(amount)
    for category, amount in goals:
        report += f'{category} - {format_number_with_dots(str(amount))} рублей\n'
        if category in exp:
            differ = amount - exp[category]
        else:
            differ = amount
        if differ >= 0:
            report += f'лимит не превышен!\n'
        else:
            report += f'лимит превышен на' \
                      f'{format_number_with_dots(str(abs(differ)))} рублей:(\n'
        report += '\n'
    await message.reply(report)


@router.message()
async def unknown_command(message: Message):
    await message.reply('я не знаю такой команды, попробуйте снова:(')


def registerr_handlers(dp: Dispatcher):
    dp.include_router(router)
