import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
from database import init_db


def generate_expense_statistics():
    # Инициализируем базу данных перед работой
    init_db()

    # Проверка существования базы данных
    db_path = os.path.join(os.path.dirname(__file__), 'expenses.db')
    if not os.path.exists(db_path):
        print(f"Ошибка: База данных {db_path} не найдена!")
        return

    # Подключение к базе данных
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return

    # Проверка содержимого базы данных
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Таблицы в базе данных:", tables)
    except sqlite3.Error as e:
        print(f"Ошибка при чтении базы данных: {e}")
        conn.close()
        return

    # Загрузка данных о расходах в DataFrame
    try:
        expenses_df = pd.read_sql_query("SELECT * FROM expenses", conn)
        
        # Проверка данных
        if expenses_df.empty:
            print("Внимание: Таблица расходов пуста!")
            return

        # Базовая статистика расходов
        print("Базовая статистика расходов:")
        print(expenses_df['amount'].describe())

        # Статистика расходов по категориям
        print("\nСредние расходы по категориям:")
        category_stats = expenses_df.groupby('category')['amount'].agg(['mean', 'sum', 'count'])
        print(category_stats)

        # Топ-5 категорий по сумме расходов
        print("\nТоп-5 категорий по сумме расходов:")
        top_categories = category_stats.sort_values('sum', ascending=False).head()
        print(top_categories)

        # Распределение расходов по месяцам
        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        monthly_expenses = expenses_df.groupby(expenses_df['date'].dt.to_period('M'))['amount'].sum()
        print("\nРасходы по месяцам:")
        print(monthly_expenses)

        # Визуализация
        plt.figure(figsize=(12, 6))
        
        # График расходов по категориям
        plt.subplot(1, 2, 1)
        category_stats['sum'].plot(kind='bar')
        plt.title('Расходы по категориям')
        plt.xlabel('Категория')
        plt.ylabel('Сумма')
        plt.xticks(rotation=45)

        # График расходов по месяцам
        plt.subplot(1, 2, 2)
        monthly_expenses.plot(kind='line')
        plt.title('Расходы по месяцам')
        plt.xlabel('Месяц')
        plt.ylabel('Сумма')
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.savefig('expense_statistics.png')
        plt.close()

    except Exception as e:
        print(f"Ошибка при работе с данными: {e}")
    finally:
        # Закрытие соединения
        conn.close()


if __name__ == '__main__':
    generate_expense_statistics()
