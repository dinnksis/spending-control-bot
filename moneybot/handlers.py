from aiogram import Router, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import add_expense, add_limit, get_expenses, get_limits, delete_all_data
from datetime import datetime
import registration
import global_values as gv
from global_values import checking_auth
from expenses_pie_chart import making_pie_charts


router = Router()
# объект, который будет использоваться для регистрации обработчиков команд и сообщений


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
    waiting_for_limit_category = State()
    waiting_for_limit_amount = State()


# клавиатура
buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='добавить трату'), KeyboardButton(text='установить лимит')],
        [KeyboardButton(text='статистика расходов'), KeyboardButton(text='лимиты')],
        [KeyboardButton(text='помощь'), KeyboardButton(text='круговая диаграмма расходов')],
        [KeyboardButton(text='выйти из аккаунта'), KeyboardButton(text='удалить данные')]
    ],
    resize_keyboard=True
)


# обработчики
# выход из аккаунта
@router.message(lambda message: message.text and message.text.lower() == 'выйти из аккаунта')
async def goodbye(message: Message):
    gv.login[message.from_user.id] = ''
    gv.is_authorized[message.from_user.id] = False
    await message.answer('вы вышли из системы. пожалуйства, войдите в систему или зарегистрируйтесь',
                         reply_markup=registration.main_buttons)


# обработчик команды /help и помощь, если человек авторизирован
@router.message(lambda message: message.text and (message.text.lower() == '/help' or message.text == 'помощь')
                and checking_auth(message.from_user.id))
async def send_help(message: Message):
    await message.reply('''вы запустили бота счетчика расходов. возможные действия:

добавить трату - добавление потраченной суммы

установить лимит - установка суммы, которую вы готовы потратить на данную категорию

статистика расходов - ваши расходы по всем добавленным категориям и то, превышены ли лимиты

лимиты - список установленных ограничений и то, превышены ли они на данный момент

круговая диаграмма расходов - изображение процентного соотношения расходов по категориям

удалить данные - удаление всех лимитов и расходов данного аккаунта''', reply_markup=buttons)


# обработчик команды /help и помощь, если человек не авторизирован
@router.message(lambda message: message.text and (message.text.lower() == '/help' or message.text.lower() == 'помощь'))
async def send_help(message: Message):
    await message.reply('''вы запустили бота счетчика расходов. возможные действия:

добавить трату - добавление потраченной суммы

установить лимит - установка суммы, которую вы готовы потратить на данную категорию

статистика расходов - ваши расходы по всем добавленным категориям и то, превышены ли лимиты

лимиты - список установленных ограничений и то, превышены ли они на данный момент

круговая диаграмма расходов - изображение процентного соотношения расходов по категориям

удалить данные - удаление всех лимитов и расходов данного аккаунта

но сначала вам надо зарегистрироваться или войти в аккаунт, до этого кнопки работать не будут :<''')


# обработчик всех остальных сообщений, если человек не авторизирован
@router.message(lambda message: not checking_auth(message.from_user.id))
async def not_authorized(message: Message):
    await message.reply('пожалуйста, сначала войдите в аккаунт или зарегистрируйтесь!')


# круговая диаграмма
@router.message(lambda message: message.text and message.text.lower() == 'круговая диаграмма расходов')
async def pie_chart(message: Message):
    user_login = gv.login[message.from_user.id]

    pie_chart_path = f'{user_login}_pie_chart.png'

    # создаем круговую диаграмму и сохраняем в файл
    result = making_pie_charts(user_login, save_path=pie_chart_path)

    if result is False:
        await message.answer('у вас нет данных для создания диаграммы. Добавьте расходы.')
    else:
        # используем FSInputFile для отправки изображения
        input_file = FSInputFile(pie_chart_path)  # FSInputFile работает с файлом на диске
        await message.answer_photo(input_file, caption='ваши расходы по категориям')


# обработчик команды добавления траты
@router.message(lambda message: message.text and (message.text.lower() == 'добавить трату'))
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
        await state.set_state(Form.waiting_for_expense_category)
        # переводит в состотяние ожидания категории расхода
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
    add_expense(gv.login[message.from_user.id], amount, category.lower(), date)

    await message.answer('трата добавлена!')
    await state.clear()


# обработчик команды добавления лимита
@router.message(lambda message: message.text and message.text.lower() == 'установить лимит')
async def start_setting_limit(message: Message, state: FSMContext):
    await message.answer('введите категорию лимита:')
    await state.set_state(Form.waiting_for_limit_category)


# ожидание ввода категории лимита
@router.message(Form.waiting_for_limit_category)
async def process_limit_category(message: Message, state: FSMContext):
    category = message.text.strip()
    await state.update_data(limit_category=category)
    await message.answer('введите сумму лимита:')
    await state.set_state(Form.waiting_for_limit_amount)


# ожидание ввода суммы лимита
@router.message(Form.waiting_for_limit_amount)
async def process_limit_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
        data = await state.get_data()
        category = data['limit_category']
        date = datetime.now().strftime('%Y-%m-%d')

        # сохранение в базу данных
        result_message = add_limit(gv.login[message.from_user.id], category.lower(), amount, date)

        await message.answer(result_message)
        await state.clear()
    except ValueError:
        await message.reply('пожалуйста, введите корректную положительную сумму.')


# обработчик команды удаления всех данных
@router.message(lambda message: message.text and message.text.lower() == 'удалить данные')
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


# удаление данных после подтверждения
@router.callback_query(lambda callback_query: callback_query.data == 'confirm_delete')
async def confirm_delete_callback(callback_query: CallbackQuery):
    delete_all_data(gv.login[callback_query.from_user.id])  # используем callback_query для получения user.id
    await callback_query.message.edit_text('ваши данные успешно удалены.')
    await callback_query.answer()


# отмена удаления данных
@router.callback_query(lambda c: c.data == 'cancel_delete')
async def cancel_delete_callback(callback_query: CallbackQuery):
    await callback_query.message.edit_text('удаление данных отменено.')
    await callback_query.answer()


# обработчик команды вывода статистики расходов
@router.message(lambda message: message.text and message.text.lower() == 'статистика расходов')
async def report_handler(message: Message):
    expenses = get_expenses(gv.login[message.from_user.id])
    limits = get_limits(gv.login[message.from_user.id])
    if not expenses:
        await message.reply('у вас нет расходов.')
        return
    report = 'ваши расходы:\n\n'
    datee = dict()
    dateg = dict()
    all_expenses = 0
    if limits:
        for category, amount in limits:
            dateg[category] = float(amount)
    for amount, category, date in expenses:
        if category in datee:
            datee[category] += float(amount)
        else:
            datee[category] = float(amount)
    for key, value in datee.items():
        report += f'{key} - {format_number_with_dots(str(value))} руб.\n'
        all_expenses += value
        if key in dateg:
            difference = value - dateg[key]
            if difference > 0:
                report += f'лимит {format_number_with_dots(str(dateg[key]))} руб. ' \
                          f'превышен на {format_number_with_dots(str(difference))} руб.\n'
            else:
                report += f'лимит {format_number_with_dots(str(dateg[key]))} руб. не превышен. ' \
                          f'до превышения лимита {format_number_with_dots(str(abs(difference)))} руб.\n'
        else:
            report += f'лимит для категории отсутствует\n'
        report += '\n'
    report += f'сумма расходов по всем категориям: {format_number_with_dots(str(all_expenses))} руб.'
    await message.reply(report)


# обработчик вывода списка лимитов
@router.message(lambda message: message.text and message.text.lower() == 'лимиты')
async def listlimits_handler(message: Message):
    limits = get_limits(gv.login[message.from_user.id])
    expenses = get_expenses(gv.login[message.from_user.id])
    if not limits:
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
    for category, amount in limits:
        report += f'{category} - {format_number_with_dots(str(amount))} руб.\n'
        if category in exp:
            differ = amount - exp[category]
        else:
            differ = amount
        if differ >= 0:
            report += f'лимит не превышен!\n'
        else:
            report += f'лимит превышен на ' \
                      f'{format_number_with_dots(str(abs(differ)))} руб.\n'
        report += '\n'
    await message.reply(report)


@router.message()
async def unknown_command(message: Message):
    await message.reply('я не знаю такой команды, попробуйте снова:(')


def registerr_handlers(dp: Dispatcher):
    dp.include_router(router)
