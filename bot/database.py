import sqlite3
from contextlib import closing


def init_db(): # инициализация бд и создание таблиц
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    category TEXT,
                    date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    category TEXT,
                    amount REAL,
                    date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            cur.execute(''' 
                CREATE TABLE IF NOT EXISTS safety (
                    login TEXT,
                    password TEXT
                )
            ''')
            conn.commit() # сохраняет изменения


def add_user(user_id, username):
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
                (user_id, username)
            )
            conn.commit()


def add_expense(user_id, amount, category, date):
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)',
                (user_id, amount, category, date)
            )
            conn.commit()


def get_expenses(user_id):
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'SELECT amount, category, date FROM expenses WHERE user_id = ?',
                (user_id,)
            )
            expenses = cur.fetchall()
    return expenses


def get_goals(user_id):
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'SELECT category, amount FROM goals WHERE user_id = ?',
                (user_id,)
            )
            goals = cur.fetchall()
    return goals


def add_goal(user_id, category, amount, date):
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'SELECT 1 FROM goals WHERE user_id = ? AND category = ?', (user_id, category)
            )
            result = cur.fetchone()
            if result:
                cur.execute(
                    'UPDATE goals SET amount = ?, date = ? WHERE user_id = ? AND category = ?',
                    (amount, date, user_id, category)
                )
                conn.commit()
                return f'лимит {category} обновлен.'
            else:
                cur.execute(
                    'INSERT INTO goals (user_id, category, amount, date) VALUES (?, ?, ?, ?)',
                    (user_id, category, amount, date)
                )
                conn.commit()
                return f'лимит {category} добавлен.'


def delete_all_data(user_id):
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('DELETE FROM expenses WHERE user_id = ?', (user_id,))
            cur.execute('DELETE FROM goals WHERE user_id = ?', (user_id,))
            conn.commit()
