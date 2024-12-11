import sqlite3
from contextlib import closing
import os

def init_db() -> None:
    # инициализация бд и создание таблиц
    db_path = os.path.join(os.path.dirname(__file__), 'expenses.db')
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('''            
                CREATE TABLE IF NOT EXISTS users (
                    login TEXT PRIMARY KEY,
                    password TEXT
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL,
                    login TEXT,
                    category TEXT,
                    date TEXT,
                    FOREIGN KEY (login) REFERENCES users (login)
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    amount REAL,
                    login TEXT,
                    date TEXT,
                    FOREIGN KEY (login) REFERENCES users (login)
                )
            ''')
            conn.commit() # сохраняет изменения


def add_user(login: str, password: str) -> None:
    db_path = os.path.join(os.path.dirname(__file__), 'expenses.db')
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'INSERT INTO users (login, password) VALUES (?, ?)',
                (login, password)
            )
            conn.commit()


def add_expense(login: str, amount: float, category: str, date: str) -> None:
    db_path = os.path.join(os.path.dirname(__file__), 'expenses.db')
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'INSERT INTO expenses (login, amount, category, date) VALUES (?, ?, ?, ?)',
                (login, amount, category, date)
            )
            conn.commit()


def get_expenses(login: str) -> list[tuple[float, str, str]]:
    db_path = os.path.join(os.path.dirname(__file__), 'expenses.db')
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'SELECT amount, category, date FROM expenses WHERE login = ?',
                (login,)
            )
            expenses = cur.fetchall()
    return expenses


def get_goals(login: str) -> list[tuple[str, float]]:
    db_path = os.path.join(os.path.dirname(__file__), 'expenses.db')
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'SELECT category, amount FROM goals WHERE login = ?',
                (login,)
            )
            goals = cur.fetchall()
    return goals


def add_goal(login: str, category: str, amount: float, date: str) -> str:
    db_path = os.path.join(os.path.dirname(__file__), 'expenses.db')
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'SELECT 1 FROM goals WHERE login = ? AND category = ?', (login, category)
            )
            result = cur.fetchone()
            if result:
                cur.execute(
                    'UPDATE goals SET amount = ?, date = ? WHERE login = ? AND category = ?',
                    (amount, date, login, category)
                )
                conn.commit()
                return f'лимит {category} обновлен.'
            else:
                cur.execute(
                    'INSERT INTO goals (login, category, amount, date) VALUES (?, ?, ?, ?)',
                    (login, category, amount, date)
                )
                conn.commit()
                return f'лимит {category} добавлен.'


def delete_all_data(login: str) -> None:
    db_path = os.path.join(os.path.dirname(__file__), 'expenses.db')
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('DELETE FROM expenses WHERE login = ?', (login,))
            cur.execute('DELETE FROM goals WHERE login = ?', (login,))
            conn.commit()
