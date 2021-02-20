# database.py
import sqlite3
import datetime
import re
from passlib.context import CryptContext
from passlib.hash import pbkdf2_sha256

connection = sqlite3.connect("useri.db", timeout=10)
cursor = connection.cursor()


class DataBase:
    def __init__(self, filename):
        self.cursor = cursor
        self.filename = filename
        self.users = None
        self.file = None
        self.load()

    def load(self):
        cursor.execute("DELETE FROM codes WHERE datee!=(SELECT date('now'))")
        connection.commit()
        self.file = open(self.filename, "r")
        self.users = {}

        for line in self.file:
            if line != "\n":
                email, password, name, created = line.strip().split(";")
                self.users[email] = (email, password, name, created)

        self.file.close()

    def get_user(self, email):
        print(*cursor.execute("SELECT email" + " FROM users WHERE email='" + email + "' ;"))
        print(email)
        if re.search(email, str(*cursor.execute("SELECT email" + " FROM users WHERE email='" + email + "' ;"))):
            unpack_user = [i for i in cursor.execute("SELECT * FROM users WHERE email='" + email + "';")]
            for user_prop in unpack_user:
                for passw in user_prop:
                    if passw.startswith("$"):
                        return passw
        else:
            return -1

    def get_user_info(self, email):
        if re.search(email, str(*cursor.execute("SELECT email" + " FROM users WHERE email='" + email + "' ;"))):
            unpack_user = [i for i in cursor.execute("SELECT * FROM users WHERE email='" + email + "';")]
            for user_prop in unpack_user:
                return user_prop

    def add_user(self, email, password, name):
        if email.strip() not in self.users:
            self.users[email.strip()] = (email.strip(), password.strip(), name.strip(), DataBase.get_date())
            self.save()
            return 1
        else:
            print("Email exists already")
            return -1

    def validate(self, email, password):
        if self.get_user(email) != -1:
            if pbkdf2_sha256.verify(password, self.get_user(email)):
                return True
            else:
                return False
        else:
            return False

    def save(self):

        with open(self.filename, "w") as f:
            for user in self.users:
                passw = self.users[user][1]
                hash_passw = pbkdf2_sha256.hash(passw)

                cursor.execute("INSERT INTO users VALUES (?,?,?,?)",
                               (self.users[user][0], hash_passw, self.users[user][2], self.users[user][3]))
                connection.commit()

    @staticmethod
    def get_date():
        return str(datetime.datetime.now()).split(" ")[0]
