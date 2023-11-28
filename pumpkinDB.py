import sqlite3

class PumpkinDB:
    def __init__(self, db) -> None:
        self.__db = db
        self.__cursor = db.cursor()


    def removeTask(self, id: int) -> bool:
        try:
            sql = "delete from tasks where id = ?"
            self.__cursor.execute(sql, (id,))
            self.__db.commit()
            return True

        except sqlite3.Error as e:
            print(str(e))
            return False

    def getTaskByTitle(self, username: str, title: str) -> bool:
        try:
            sql = "select * from tasks where username like ? and title like ? limit 1"
            self.__cursor.execute(sql, (username, title))
            res = self.__cursor.fetchone()

            if not res:
                return False

            return res

        except sqlite3.Error as e:
            print(f"Error while receiving user task by title:\n{e}")
            return False

    def getTasks(self, username: str):
        try:
            sql = "select * from tasks where username like ?"
            self.__cursor.execute(sql, (username,))
            res = self.__cursor.fetchall()

            if not res:
                return (False, f"You don't have any tasks, {username}")

            return res

        except sqlite3.Error as e:
            print(f"Error while receiving user tasks:\n{e}")
            return (False, "Database error!")

    def addTask(self, title: str, description: str, username: str) -> bool:
        try:
            sql = "insert into tasks values (null, ?, ?, ?)"
            self.__cursor.execute(sql, (title, description, username))
            self.__db.commit()

        except sqlite3.Error as e:
            print(f"Error while adding task to database:\n{e}")
            return False

        return True

    def getUserByID(self, user_id: str) -> tuple | bool:
        try:
            sql = "select * from users where id = ? limit 1"
            self.__cursor.execute(sql, (int(user_id),))
            res = self.__cursor.fetchone()

            if not res:
                return (False, "There's no user wth such id!")

            return res

        except sqlite3.Error as e:
            return (False, "Database error!")

    def getUser(self, username: str) -> tuple | bool:
        try:
            sql = "select * from users where username = ? limit 1"
            self.__cursor.execute(sql, (username,))
            res = self.__cursor.fetchone()

            if not res:
                return (False, "There's no user wth such username!")

            return res
        except sqlite3.Error as e:
            return (False, "Database error!")

    def addUser(self, username: str, password: str) -> tuple:
        self.__cursor.execute(f"select count() as count FROM users where username like ?", (username,))

        user_exists = self.__cursor.fetchone()['count'] > 0

        if user_exists:
            return (False, "User with such username already exists!")

        try:
            sql = "insert into users values(null, ?, ?)"
            self.__cursor.execute(sql, (username, password))
            self.__db.commit()
        except sqlite3.Error as e:
            print(f"Error while adding new user to database:\n{e}")
            return (False, "Database error!")

        return (True, "User signed up successfully!")
