import sqlite3
from contextlib import closing


# инициализация бд и создание таблиц
def init_db() -> None:
    with sqlite3.connect('expenses.db') as conn:
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
                CREATE TABLE IF NOT EXISTS limits (
                    limit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    amount REAL,
                    login TEXT,
                    date TEXT,
                    FOREIGN KEY (login) REFERENCES users (login)
                )
            ''')
            conn.commit()
            # сохраняет изменения


# добавление аккаунта
def add_user(login: str, password: str) -> None:
    with sqlite3.connect('expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'INSERT INTO users (login, password) VALUES (?, ?)',
                (login, password)
            )
            conn.commit()


# добавление траты
def add_expense(login: str, amount: float, category: str, date: str) -> None:
    with sqlite3.connect('expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'INSERT INTO expenses (login, amount, category, date) VALUES (?, ?, ?, ?)',
                (login, amount, category, date)
            )
            conn.commit()


# возвращение всех трат по логину
def get_expenses(login: str) -> list[tuple[float, str, str]]:
    with sqlite3.connect('expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'SELECT amount, category, date FROM expenses WHERE login = ?',
                (login,)
            )
            expenses = cur.fetchall()
    return expenses


# возвращение всех лимитов по логину
def get_limits(login: str) -> list[tuple[str, float]]:
    with sqlite3.connect('expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'SELECT category, amount FROM limits WHERE login = ?',
                (login,)
            )
            limits = cur.fetchall()
    return limits


# добавление лимита
def add_limit(login: str, category: str, amount: float, date: str) -> str:
    with sqlite3.connect('expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'SELECT 1 FROM limits WHERE login = ? AND category = ?', (login, category)
            )
            result = cur.fetchone()
            if result:
                cur.execute(
                    'UPDATE limits SET amount = ?, date = ? WHERE login = ? AND category = ?',
                    (amount, date, login, category)
                )
                conn.commit()
                return f'лимит {category} обновлен.'
            else:
                cur.execute(
                    'INSERT INTO limits (login, category, amount, date) VALUES (?, ?, ?, ?)',
                    (login, category, amount, date)
                )
                conn.commit()
                return f'лимит {category} добавлен.'


# удаление всех данных по логину
def delete_all_data(login: str) -> None:
    with sqlite3.connect('expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('DELETE FROM expenses WHERE login = ?', (login,))
            cur.execute('DELETE FROM limits WHERE login = ?', (login,))
            conn.commit()
