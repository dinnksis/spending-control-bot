import sqlite3
from contextlib import closing
import bcrypt
# для хэширования паролей


# хэшированный пароль
def add_user_to_database(login: str, password: str) -> None:
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with sqlite3.connect('expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'INSERT INTO users (login, password) VALUES (?, ?)',
                (login, hashed_pw,)
            )
            conn.commit()


# проверка, зарегистрирован ли пользователь
def is_user_registered(login: str) -> bool:
    with sqlite3.connect('expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('SELECT login FROM users WHERE login = ?', (login.lower(),))
            return cur.fetchone() is not None


# проверка пароля
def check_password(login: str, password: str) -> bool:
    with sqlite3.connect('expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('SELECT password FROM users WHERE login = ?', (login.lower(),))
            result = cur.fetchone()
            return result and bcrypt.checkpw(password.encode('utf-8'), result[0])
