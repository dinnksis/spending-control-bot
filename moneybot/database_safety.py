import sqlite3
from contextlib import closing
import bcrypt
# для хэширования паролей


#просто пароль
def user_adding(login, password):
    #hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'INSERT INTO safety (login, password) VALUES (?, ?)',
                (login, password)
            )
            conn.commit()


# Функция проверки, зарегистрирован ли пользователь
def is_user_registered(login):
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('SELECT login FROM safety WHERE login = ?', (login,))
            return cur.fetchone() is not None
import sqlite3
from contextlib import closing
import bcrypt
# для хэширования паролей


# хэшированный пароль
def add_user_to_database(login: str, password: str) -> None:
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute(
                'INSERT INTO users (login, password) VALUES (?, ?)',
                (login, hashed_pw,)
            )
            conn.commit()


# Функция проверки, зарегистрирован ли пользователь
def is_user_registered(login: str) -> bool:
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('SELECT login FROM users WHERE login = ?', (login.lower(),))
            return cur.fetchone() is not None


# Функция проверки пароля
def check_password(login: str, password: str) -> bool:
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('SELECT password FROM users WHERE login = ?', (login.lower(),))
            result = cur.fetchone()
            return result and bcrypt.checkpw(password.encode('utf-8'), result[0])


# Функция проверки пароля
def check_password(login,password):
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('SELECT password FROM safety WHERE login = ?', (login,))
            result = cur.fetchone()
            if result[0]==password:
                return True
            return False
