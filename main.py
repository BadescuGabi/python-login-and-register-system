# main.py
import sqlite3
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database import DataBase
from database import *
import re
from reset_passw import reset_passw as new_password

regex_mail = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'


class CreateAccountWindow(Screen):
    namee = ObjectProperty(None)
    code = ObjectProperty(None)
    password = ObjectProperty(None)
    confirmpassword = ObjectProperty(None)

    def submit(self):  #
        if self.namee.text != "" and self.password.text == self.confirmpassword.text:
            if re.search(self.code.text,
                         str(*db.cursor.execute("SELECT code" + " FROM codes WHERE code='" + self.code.text + "' ;"))):
                a=db.cursor.execute("SELECT email" + " FROM codes WHERE code='" + self.code.text + "' ;").fetchone()
                for email in a:
                    db.add_user(email, self.password.text, self.namee.text)

                self.reset()

                sm.current = "login"
            else:
                invalidForm()
        else:
            invalidForm()
    def login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.code.text = ""
        self.password.text = ""
        self.namee.text = ""
        self.confirmpassword.text=""


class EmailWindow2(Screen):
    email = ObjectProperty(None)

    def confirmBtn1(self):
        if re.search(regex_mail,self.email.text):
            sm.current = "create"
            new_password.send_code_new_acc(self.email.text)
            self.reset()
        else:
            invalidEmail2()
    def reset(self):
        self.email.text=""

class LoginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if db.validate(self.email.text, self.password.text):
            MainWindow.current = self.email.text
            self.reset()
            sm.current = "main"
        else:
            invalidLogin()

    def createBtn(self):
        self.reset()
        sm.current = "email2"

    def newpasswordBtn(self):
        self.reset()
        sm.current = "email"

    def reset(self):
        self.email.text = ""
        self.password.text = ""


class MainWindow(Screen):
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    email = ObjectProperty(None)
    current = ""

    def logOut(self):
        sm.current = "login"

    def on_enter(self, *args):
        email, password, name, created = db.get_user_info(self.current)
        self.n.text = "Account Name: " + name
        self.email.text = "Email: " + self.current
        self.created.text = "Created On: " + created


class Email:
    email = ObjectProperty(None)
    email_1 = ""


class EmailWindow(Screen, Email):

    def confirmBtn(self):
        sm.current = "newpassword"
        if new_password.validate_email(self.email.text):
            print(self.email.text)
            new_password.send_code(self.email.text)
            Email.email_1 = self.email.text
        else:
            invalidEmail()
            sm.current = "email"

    def login(self):
        # self.email = ""
        sm.current = "login"


class NewPasswordWindow(Screen, Email):
    code = ObjectProperty(None)
    password = ObjectProperty(None)
    confirmpassw = ObjectProperty(None)

    def new_passwBtn1(self):
        if new_password.validate_reset_passw(self.code.text, self.password.text, self.confirmpassw.text) == -1:
            invalidCode()
        elif new_password.validate_reset_passw(self.code.text, self.password.text, self.confirmpassw.text) == False:
            invalidPassw()
        """else:
            self.reset()
            sm.current = "login"
"""

    def new_passwBtn2(self):
        self.reset()
        new_password.send_code(Email.email_1)
        sm.current = "newpassword"

    def reset(self):
        # self.code.text = ""
        self.password.text = ""
        self.confirmpassw.text = ""

    def login(self):
        self.code = ""
        self.password = ""
        self.confirmpassw = ""
        sm.current = "login"


class WindowManager(ScreenManager):
    pass


# ==================================================================================================================
#                                   POPUP-URI
# ==================================================================================================================

def invalidLogin():
    pop = Popup(title='Invalid Login',
                content=Label(text='Invalid username or password.'),
                size_hint=(None, None), size=(400, 400))
    pop.open()


def invalidForm():
    pop = Popup(title='Invalid Form',
                content=Label(text='Please fill in all inputs with valid information.'),
                size_hint=(None, None), size=(400, 400))

    pop.open()


def invalidPassw():
    pop = Popup(title="Invalid password",
                content=Label(text="Please make sure the passwords are the same"),
                size_hint=(None, None), size=(400, 400))
    pop.open()


def invalidCode():
    pop = Popup(title="Invalid code",
                content=Label(text="Code incorectly"),
                size_hint=(None, None), size=(400, 400))
    pop.open()


def invalidEmail():
    pop = Popup(title="Invalid email",
                content=Label(text="This email doesn't have an account"),
                size_hint=(None, None), size=(400, 400))
    pop.open()

def invalidEmail2():
    pop = Popup(title="Invalid email",
                content=Label(text="Enter a valid email"),
                size_hint=(None, None), size=(400, 400))
    pop.open()

def ResendConfirmed():
    pop = Popup(title="Code",
                content=Label(text="Code resended succesfully"),
                size_hint=(None, None), size=(400, 400))
    pop.open()


kv = Builder.load_file("my.kv")

sm = WindowManager()
db = DataBase("users.txt")
db.load()
screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"), MainWindow(name="main"),
           NewPasswordWindow(name="newpassword"), EmailWindow(name="email"), EmailWindow2(name="email2")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"


class MyMainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()
