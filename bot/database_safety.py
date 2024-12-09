import sqlite3
from contextlib import closing
import bcrypt # для хэширования паролей


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


# Функция проверки пароля
def check_password(login,password):
    with sqlite3.connect('../moneybot/expenses.db') as conn:
        with closing(conn.cursor()) as cur:
            cur.execute('SELECT password FROM safety WHERE login = ?', (login,))
            result = cur.fetchone()
            if result[0]==password:
                return True
            return False
