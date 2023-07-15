import aiomysql


class MySqlDatabase:
    
    async def create_table():
        async with aiomysql.connect(host="90.156.209.160",
        user="gen_user",
        passwd="A!2XggF\Q)wcjw",
        db="default_db",
        port=3306) as con:
            c = await con.cursor
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
            await con.commit()

