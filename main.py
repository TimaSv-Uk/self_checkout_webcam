from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivy.lang import Builder

import pyodbc

from ProductList import ProductList
from camera import MyCamera
from MDlog import MyMDLog


class Menu(Screen):
    def get_menu_items(self):
        if MDApp.get_running_app().role == "Cashier":
            self.ids.app_bar.right_action_items = [
                [
                    "cart-outline",
                    lambda x: self.open_screan("main"),
                    "main",
                ],
                [
                    "list-box",
                    lambda x: self.open_screan("catalogue"),
                    "catalogue",
                ],
            ]
        elif MDApp.get_running_app().role == "Manager":
            self.ids.app_bar.right_action_items = [
                [
                    "cart-outline",
                    lambda x: self.open_screan("main"),
                    "main",
                ],
                [
                    "list-box",
                    lambda x: self.open_screan("catalogue"),
                    "catalogue",
                ],
                [
                    "format-list-bulleted-square",
                    lambda x: self.open_screan("catalogue"),
                    "add invoice",
                ],
            ]

    def open_screan(self, screan_name: str):
        MDApp.get_running_app().change_screen(screan_name)
        self.ids.app_bar.right_action_items = [
            ["menu", lambda x: self.get_menu_items(), "menu"],
        ]


class CatalogWindow(Screen):
    pass


class LoginWindow(Screen):
    pass


class ScanWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


Builder.load_file("MDlog.kv")
Builder.load_file("ProductList.kv")
Builder.load_file("camera.kv")


class MainApp(MDApp):
    role = ""

    def build(self):
        return Builder.load_file("screen_manager.kv")

    def change_screen(self, screan_name: str):
        self.root.current = screan_name

    def connect_to_db(self, username: str, password: str):
        # DRIVER=ODBC Driver 17 for SQL Server;SERVER=GIORNO\SQLEXPRESS;DATABASE=AUTO_CASHIER;
        # self.USERNAME = username
        # self.PASSWORD = password

        # text cashier
        # self.PASSWORD = "bob"
        # self.USERNAME = "bob"

        # text manager
        self.USERNAME = "nick"
        self.PASSWORD = "0000"
        try:
            file = open("connect.txt", "r")
            connection_string = file.readline()
            self.conn = pyodbc.connect(
                connection_string + f"UID={self.USERNAME};PWD={self.PASSWORD}"
            )
            self.cursor = self.conn.cursor()
            self.set_user_role()
            self.change_screen("main")
            # self.change_screen("catalogue")

        except Exception:
            MDSnackbar(
                MDLabel(
                    text="Invalid user name or password",
                ),
            ).open()

    def set_user_role(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"EXEC GET_USER_ROLE '{self.USERNAME}';")
        self.role = self.cursor.fetchone()[0]

    def select_as_dick(self, query: str):
        try:
            self.cursor.execute(query)
            records = []
            columns = [column[0] for column in self.cursor.description]
            records = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            return records
        except Exception:
            MDSnackbar(
                MDLabel(
                    text="Error",
                ),
            ).open()
            return []

    def execute(self, query: str):
        try:
            self.cursor.execute(query)
            self.conn.commit()
        except Exception as e:
            MDSnackbar(
                MDLabel(
                    text=e,
                ),
            ).open()


MainApp().run()
