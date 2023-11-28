from flask_login import UserMixin


class UserLogin(UserMixin):

    def login(self, user):
        self.__user = user
        return self

    def logout(self):
        self.__user = None

    def fromDB(self, user_id, db):
        self.__user = db.getUserByID(user_id)
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_username(self):
        return str(self.__user['username'])
