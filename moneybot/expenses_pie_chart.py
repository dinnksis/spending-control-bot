import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import sqlite3
import pandas as pd


def beautiful_number(number_str: str) -> str:
    parts = number_str.split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else ''
    reversed_integer = integer_part[::-1]
    formatted_reversed_integer = '.'.join(reversed_integer[i:i + 3] for i in range(0, len(reversed_integer), 3))
    formatted_integer = formatted_reversed_integer[::-1]
    if decimal_part:
        return f'{formatted_integer},{decimal_part}'
    else:
        return formatted_integer


def making_pie_charts(user_login, save_path=None):
    if save_path is None:
        save_path = f"{user_login}_pie_chart.png"

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    query = """
    SELECT category, SUM(amount) as total_amount
    FROM expenses
    WHERE login = ?
    GROUP BY category
    """

    cursor.execute(query, (user_login,))
    data = cursor.fetchall()

    # cоздаем DataFrame из результата запроса
    expenses_df = pd.DataFrame(data, columns=['category', 'total_amount'])
    conn.close()

    if expenses_df.empty:
        return False

    # подготавливаем данные для графика
    categories = expenses_df['category']
    amounts = expenses_df['total_amount']
    labels = [f"{cat} ({beautiful_number(str(amt))} руб.)" for cat, amt in zip(categories, amounts)]

    # создаем градиентную палитру в синих, фиолетовых и розовых тонах
    custom_colors = mcolors.LinearSegmentedColormap.from_list(
        "custom_palette",
        ["#1f77b4", "#6a0dad", "#ff69b4"]  # Синий -> Фиолетовый -> Розовый
    )
    colors = [custom_colors(i / len(categories)) for i in range(len(categories))]

    # строим график
    plt.figure(figsize=(8, 8))
    plt.pie(
        amounts,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors  # устанавливаем цвета
    )
    plt.title('соотношение сумм трат по категориям', fontsize=14, color='darkblue')

    plt.savefig(save_path)
    plt.close()  # закрываем график

    return save_path  # возвращаем путь к сохраненному графику
