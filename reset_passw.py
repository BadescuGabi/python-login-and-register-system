# reset password
import sqlite3
import re
import yagmail
import random
import string
import datetime
from passlib.hash import pbkdf2_sha256
import database as db


def generate_code():
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(8)))
    return result_str


class reset_passw:
    code = ""

    @classmethod
    def send_code(self, receiver):
        self.code=generate_code()
        yag = yagmail.SMTP("agendaaa123@gmail.com")
        yag.send(
            to=receiver,
            subject="Resetare parola",
            contents="Pentru resetarea parolei introduceti codul: " + self.code,
        )
        self.add_to_codes(receiver, self.get_date(), self.code)

    @classmethod
    def send_code_new_acc(self, receiver):
        self.code=generate_code()
        yag = yagmail.SMTP("agendaaa123@gmail.com")
        yag.send(
            to=receiver,
            subject="Confirmare cont",
            contents="Pentru confirmarea creeari contului introduceti codul:" + self.code+" (valabil in decursul zilei de azi",
        )
        self.add_to_codes(receiver, self.get_date(), self.code)

    @classmethod
    def get_code(cls):
        return cls.code

    @staticmethod
    def get_date():
        return str(datetime.datetime.now()).split(" ")[0]

    @staticmethod
    def validate_reset_passw(code, password, conf_password):
        if re.search(code, str(*db.cursor.execute("SELECT code" + " FROM codes WHERE code='" + code + "' ;"))):
            if password == conf_password and password != "":
                unpack_mail = [i for i in db.cursor.execute("SELECT email FROM codes WHERE code='" + code + "';")]
                user_mail = ""
                for mail in unpack_mail:
                    user_mail = mail[0]

                hash_passw = pbkdf2_sha256.hash(password)
                db.cursor.execute("UPDATE users "
                                  "SET password='" + hash_passw + "'"
                                                                  "WHERE email='" + user_mail + "';")
                return True
            else:
                return False
        else:
            return -1

    @staticmethod
    def get_mail_cod(code): #cauta mail dupa cod
        if re.search(code, str(*db.cursor.execute("SELECT code" + " FROM codes WHERE code='" + code + "' ;"))):
                unpack_mail = [i for i in db.cursor.execute("SELECT email FROM codes WHERE code='" + code + "';")]
                user_mail = ""
                for mail in unpack_mail:
                    user_mail = mail[0]
                    return  user_mail

    @staticmethod
    def validate_email(email):
        if re.search(email, str(*db.cursor.execute("SELECT email" + " FROM users WHERE email='" + email + "' ;"))):
            return True
        else:
            return False

    @staticmethod
    def add_to_codes(email, date, code):

        if re.search(email, str(*db.cursor.execute("SELECT email" + " FROM codes WHERE email='" + email + "' ;"))):
            print(str(*db.cursor.execute("SELECT email" + " FROM codes WHERE email='" + email + "' ;")))
            db.cursor.execute("UPDATE codes " +
                              "SET code='" + code + "'" +
                              "WHERE email='" + email + "';")
            db.connection.commit()

        else:
            db.cursor.execute("INSERT INTO codes VALUES (?,?,?)", (email, date, code))
            db.connection.commit()
            db.connection.commit()
