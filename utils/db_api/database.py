from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
            self,
            command,
            *args,
            fetch: bool = False,
            fetchval: bool = False,
            fetchrow: bool = False,
            execute: bool = False
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE,
        phone VARCHAR(20),
        role VARCHAR (100)
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id, phone='null', role='null'):
        sql = "INSERT INTO users (full_name, username, telegram_id, phone, role) " \
              "VALUES($1, $2, $3, $4, $5) returning *"
        return await self.execute(sql, full_name, username, telegram_id, phone, role, fetchrow=True)

    async def update_user_name(self, telegram_id, name):
        telegram_id = str(telegram_id)
        sql = f"UPDATE Users SET full_name='{name}' WHERE telegram_id='{telegram_id}'"
        return await self.execute(sql, execute=True)

    async def update_user_phone(self, telegram_id, phone):
        telegram_id = str(telegram_id)
        sql = f"UPDATE Users SET phone='{phone}' WHERE telegram_id='{telegram_id}'"
        return await self.execute(sql, execute=True)

    async def getUser_name(self, telegram_id):
        telegram_id = str(telegram_id)
        sql = f"SELECT full_name FROM Users WHERE telegram_id='{telegram_id}'"
        return await self.execute(sql, fetchval=True)

    async def getUser_phone(self, telegram_id):
        telegram_id = str(telegram_id)
        sql = f"SELECT phone FROM Users WHERE telegram_id='{telegram_id}'"
        return await self.execute(sql, fetchval=True)

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_user(self, telegram_id):
        sql = f"SELECT * FROM Users WHERE telegram_id = '{telegram_id}'"
        return await self.execute(sql, fetchrow=True)

    async def get_user_role(self, telegram_id):
        sql = f"SELECT role FROM Users WHERE telegram_id = '{telegram_id}'"
        return await self.execute(sql, fetchrow=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def delete_user_by_id(self, telegram_id):
        await self.execute(f"DELETE FROM Users WHERE telegram_id = '{telegram_id}'", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)

    ####### TEACHER #######

    async def create_table_teachers(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Teachers (
        teacher_id SERIAL PRIMARY KEY,
        teacher_name VARCHAR(50),
        contact_number VARCHAR(15)
        );
        """

        await self.execute(sql, execute=True)

    async def add_teacher(self, teacher_name, number):
        sql = f"""
            INSERT INTO Teachers (teacher_name, contact_number) VALUES($1, $2) returning * """
        return await self.execute(sql, teacher_name, number, fetchrow=True)

    async def get_all_teachers(self):
        sql = f"""
        SELECT teacher_name from Teachers
        """
        return await self.execute(sql, fetch=True)

    async def get_teacher_name(self, name):
        sql = f"SELECT * FROM Teachers WHERE teacher_name = '{name}'"
        return await self.execute(sql, fetchrow=True)

    async def delete_teacher_by_name(self, name):
        await self.execute(f"DELETE FROM Teachers WHERE teacher_name = '{name}'", execute=True)

    async def drop_teachers(self):
        await self.execute("DROP TABLE Teachers", execute=True)

    ###### GROUP #######

    async def create_table_groups(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Groups (
        group_id SERIAL PRIMARY KEY,
        group_name VARCHAR(50),
        group_teacher VARCHAR(255)
        );

        """
        await self.execute(sql, execute=True)

    async def add_group(self, group_name, group_teacher):
        sql = f"""
        INSERT INTO Groups (group_name, group_teacher) VALUES($1, $2) returning *

        """
        return await self.execute(sql, group_name, group_teacher, fetchrow=True)

    async def get_all_groups(self):
        sql = f"""
        SELECT group_name from Groups
        """
        return await self.execute(sql, fetch=True)



    async def get_group_name_by_teacher(self, teacher_name):
        sql = f"""
        SELECT group_name from Groups WHERE group_teacher = '{teacher_name}'
        """
        return await self.execute(sql, fetchrow=True)

    async def delete_group_by_name(self, name):
        await self.execute(f"DELETE FROM Groups WHERE group_name = '{name}'", execute=True)

    async def delete_group_by_teacher(self, name):
            await self.execute(f"DELETE FROM Groups WHERE group_teacher = '{name}'", execute=True)

    async def drop_groups(self):
        await self.execute("DROP TABLE Groups", execute=True)

    ####### CHILDREN ##########

    async def create_table_children(self):
        sql = """  
        CREATE TABLE IF NOT EXISTS Children (
    child_id SERIAL PRIMARY KEY,
    child_name VARCHAR(50),
    reg_date VARCHAR (244),
    group_name VARCHAR(100),
    photo_path VARCHAR(1000),
    vznos INTEGER
    );
        """

        await self.execute(sql, execute=True)

    async def add_child(self, child_name, reg_date, group, photo_path, vznos):
        sql = """
        INSERT INTO Children (child_name, reg_date, group_name, photo_path, vznos)
        VALUES($1, $2, $3, $4, $5)
        RETURNING *
        """
        return await self.execute(sql, child_name, reg_date, group, photo_path, vznos, fetchrow=True)

    async def get_children_byGroup(self, group_name):
        sql = f"SELECT child_name FROM Children WHERE group_name = '{group_name}'"
        return await self.execute(sql, fetch=True)

    async def get_Allchildren_byGroup(self, group_name):
        sql = f"SELECT * FROM Children WHERE group_name = '{group_name}'"
        return await self.execute(sql, fetch=True)

    async def get_child_by_name(self, name):
        sql = f"SELECT * FROM Children WHERE child_name = '{name}'"
        return await self.execute(sql, fetchrow=True)

    async def get_all_children(self):
        sql = f"SELECT child_name FROM Children"
        return await self.execute(sql, fetch=True)

    async def count_ch_by_group(self, group_name):
        sql = f"SELECT COUNT(*) FROM Children WHERE group_name = '{group_name}'"
        return await self.execute(sql, fetchval=True)

    async def is_Child(self, name):
        sql = f"SELECT child_name FROM Children WHERE child_name = '{name}'"
        return await self.execute(sql, fetchrow=True)

    async def get_child_vznos(self, id):
        sql = f"SELECT vznos FROM Children WHERE child_id = '{id}'"
        return await self.execute(sql, fetchrow=True)

    async def get_child_name_id(self, bola_id):
        sql = f"SELECT child_name FROM Children WHERE child_id = '{bola_id}'"
        return await self.execute(sql, fetchrow=True)

    async def get_child_regdate_id(self, bola_id):
        sql = f"SELECT reg_date FROM Children WHERE child_id = '{bola_id}'"
        return await self.execute(sql, fetchrow=True)

    async def get_child_group_id(self, bola_id):
        sql = f"SELECT group_name FROM Children WHERE child_id = '{bola_id}'"
        return await self.execute(sql, fetchrow=True)

    async def count_children(self):
        sql = f"SELECT COUNT(*) FROM Children"
        return await self.execute(sql, fetchrow=True)



    #

    async def delete_child_by_name(self, name):
        await self.execute(f"DELETE FROM Children WHERE child_name = '{name}'", execute=True)

    async def delete_children_by_Group(self, name):
            await self.execute(f"DELETE FROM Children WHERE group_name = '{name}'", execute=True)

    async def drop_children(self):
        await self.execute("DROP TABLE Children", execute=True)

    async def create_table_attendance(self):
        sql = f"""
    CREATE TABLE IF NOT EXISTS Attendance (
    attendance_id SERIAL PRIMARY KEY,
    child_id INTEGER,
    attendance_date VARCHAR(100),
    status INTEGER,
    qarz INTEGER
    );
"""

        await self.execute(sql, execute=True)

    async def add_attendance(self, child_id, date, status, qarz=0):
        sql = """
        INSERT INTO Attendance (child_id, attendance_date, status, qarz)
        VALUES($1, $2, $3, $4)
        RETURNING *
                """
        return await self.execute(sql, child_id, date, status, qarz, fetchrow=True)

    async def get_attendance_by_date(self, bola_id, date):
        sql = f"""
SELECT * FROM Attendance
WHERE child_id = '{bola_id}' AND attendance_date = '{date}';

"""

        return await self.execute(sql, fetch=True)

    async def get_child_Qarz(self, bola_id):
        sql = f"SELECT qarz FROM Attendance WHERE child_id = '{bola_id}'"
        return await self.execute(sql, fetchrow=True)

    async def update_child_qarz(self, qarz, bola_id):
        sql = "UPDATE Attendance SET qarz=$1 WHERE child_id=$2"
        return await self.execute(sql, qarz, bola_id, execute=True)

    async def bola_qarzi(self, bola_id):
        sql = f"""
SELECT SUM(qarz) FROM Attendance
WHERE child_id = '{bola_id}'
"""
        return await self.execute(sql, fetchrow=True)

    async def bugungi_kirim(self, date):
            sql = f"""
    SELECT SUM(qarz) FROM Attendance
    WHERE attendance_date = '{date}'
    """
            return await self.execute(sql, fetchrow=True)

    async def oylik_kirim(self):
        sql = f"""
 SELECT EXTRACT(YEAR FROM CAST(attendance_date AS DATE)) AS year, EXTRACT(MONTH FROM CAST(attendance_date AS DATE)) AS month, SUM(qarz) AS monthly_tuition
FROM Attendance
GROUP BY year, month;


        """

        return await self.execute(sql, fetchrow=True)


    async def count_todays_comed(self, date):
        sql = f"""
        SELECT COUNT(*) AS count_came_today
        FROM Attendance
        WHERE attendance_date = '{date}'
        AND status = 1
"""
        return await self.execute(sql, fetchval=True)

    async def drop_attentandance(self):
        await self.execute("DROP TABLE Attendance", execute=True)

    async def create_table_pHistory(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Payments (
        id SERIAL PRIMARY KEY,
        child_id INTEGER,
        date VARCHAR(29),
        amount INTEGER
        );
        
        """
        await self.execute(sql, execute=True)

    async def add_payment_history(self, bola_id, date, amount):
        sql = f"""
        INSERT INTO Payments (child_id, date, amount)
        VALUES($1, $2, $3)
        RETURNING *
        """
        return await self.execute(sql, bola_id, date, amount, fetchrow=True)
