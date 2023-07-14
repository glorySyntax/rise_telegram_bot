from datetime import datetime
import aiosqlite
from aiogram.types import User


class UsersDataBase:
    def __init__(self):
        self.path = 'databases/users.db'

    async def create_table(self):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute('''CREATE TABLE IF NOT EXISTS users(
                            uid INTEGER PRIMARY KEY,
                            balance INTEGER, 
                            birthday TEXT, 
                            email TEXT, 
                            phone_number TEXT, 
                            subscribe_vk INTEGER, 
                            subscribe_tg INTEGER
                            )''')
            await c.execute('''CREATE TABLE IF NOT EXISTS logs(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            uid INTEGER,
                            admin_id INTEGER,
                            count INTEGER,
                            action TEXT,
                            date TEXT,
                            reason TEXT
            )''')
            await c.execute('''CREATE TABLE IF NOT EXISTS admins(
                            uid INTEGER
            )''')
            await c.execute('''CREATE TABLE IF NOT EXISTS pages(
                            uid INTEGER,
                            page INTEGER,
                            pages INTEGER
            )''')
            await con.commit()

    async def get(self, user: User):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute('SELECT * FROM users WHERE uid =?',(user.id,))
            return await c.fetchone()
        
    async def reg_user(self, user: User,):
        async with aiosqlite.connect(self.path) as con:
            await self.add_log(user.id, 'bot', 100, '+', 
                               datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 'Регистрация')
            c = await con.cursor()
            await c.execute('INSERT INTO users (uid, balance) VALUES (?, ?)', 
                            (user.id, 100,))
            await con.commit()

    async def get_login(self, login: str):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute('SELECT * FROM users WHERE login =?',(login,))
            return await c.fetchall()
        
    async def add_log(self, user: int, admin: str, count: int, action: str, date: str, reason: str):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute('INSERT INTO logs VALUES(NULL, ?, ?, ?, ?, ?, ?)',
                            (user, admin, count, action, date, reason))
            await con.commit()
    
    async def get_admin(self, user: User):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute('SELECT * FROM admins WHERE uid =?',(user.id,))
            return await c.fetchone()

    async def add_admin(self, user: User):
        if not await self.get_admin(user):
            async with aiosqlite.connect(self.path) as con:
                c = await con.cursor()
                await c.execute('INSERT INTO admins VALUES (?)',(user.id,))
                await con.commit()
            return False
        else:
            return True
        
    async def update_user(self, user: User, value: str, item: str):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute(f'UPDATE users SET {item} =? WHERE uid =?',
                            (value, user.id,))
            await con.commit()

    async def get_payment_history(self, user: int):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute('SELECT * FROM logs WHERE uid =?',(user,))
            return await c.fetchall()
        
    async def pages(self, user: User, page: int, pages: int, action: int):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            if action == 1:
                await c.execute('SELECT * FROM pages WHERE uid =?',(user.id,))
                row = await c.fetchone()
                if not row:
                    await c.execute('INSERT INTO pages VALUES (?, ?, ?)',(user.id, page, pages,))
                elif row[1] >= row[2] or row != []:
                    await c.execute('DELETE FROM pages WHERE uid =?',(user.id,))
                    await c.execute('INSERT INTO pages VALUES (?, ?, ?)',(user.id, page, pages,))
            elif action == 2:
                await c.execute('UPDATE pages SET page = page+? WHERE uid =?',(1, user.id,))
            elif action == 3:
                await c.execute('UPDATE pages SET page = page-? WHERE uid =?',(1, user.id,))
            elif action == 4:
                await c.execute('SELECT * FROM pages WHERE uid =?',(user.id,))
                return await c.fetchone()
            elif action == 5:
                await c.execute('DELETE FROM pages WHERE uid =?',(user.id,))
            await con.commit()

    async def get2(self, user_id: int):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute('SELECT * FROM users WHERE uid =?',(user_id,))
            return await c.fetchone()
        
    async def update_balance(self, user_id: int, action: str, count: int):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute(
                f'UPDATE users SET balance = balance {action} ? WHERE uid =?',(count, user_id,))
            await con.commit()

    async def all_users(self,):
        async with aiosqlite.connect(self.path) as con:
            c = await con.cursor()
            await c.execute('SELECT uid FROM users')
            return await c.fetchall()