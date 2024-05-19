import pyodbc
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

from CashRegister import CashRegister
from MDlog import MyMDLog
from InvoiceList import InvoiceList
from ManufacturerList import ManufacturerList
from CategoryList import CategoryList
from SupplierList import SupplierList
from ProductList import ProductList
from RegisterCashier import RegisterCashier
from Analytics import Analytics


class Menu(Screen):
    def get_menu_items(self):
        if MDApp.get_running_app().role == "Cashier":
            self.ids.app_bar.right_action_items = [
                [
                    "cash-register",
                    lambda x: self.open_screan("main"),
                    "Термінал",
                ],
                [
                    "list-box",
                    lambda x: self.open_screan("catalogue"),
                    "Товари",
                ],
            ]
        elif MDApp.get_running_app().role == "Manager":
            self.ids.app_bar.right_action_items = [
                [
                    "cash-register",
                    lambda x: self.open_screan("main"),
                    "Термінал",
                ],
                [
                    "list-box",
                    lambda x: self.open_screan("catalogue"),
                    "Товари",
                ],
                [
                    "format-list-bulleted-square",
                    lambda x: self.open_screan("invoice"),
                    "Накладна",
                ],
                [
                    "factory",
                    lambda x: self.open_screan("manufacturer"),
                    "Виробник",
                ],
                [
                    "account-cash",
                    lambda x: self.open_screan("supplier"),
                    "Постачальник",
                ],
                [
                    "shape",
                    lambda x: self.open_screan("category"),
                    "Категорія",
                ],
                [
                    "account-plus",
                    lambda x: self.open_screan("register_cashier"),
                    "Додати касира",
                ],
                [
                    "poll",
                    lambda x: self.open_screan("analytics"),
                    "Звітність про продажі",
                ],
            ]

    def open_screan(self, screan_name: str):
        MDApp.get_running_app().change_screen(screan_name)
        self.ids.app_bar.right_action_items = [
            ["menu", lambda x: self.get_menu_items(), "Меню"],
        ]


class ManufacturerWindow(Screen):
    def on_pre_enter(self):
        self.ids.ManufacturerList.open_manufacturer_list()
        self.ids.ManufacturerList.open_new_manufacturer_form()


class SupplierWindow(Screen):
    def on_pre_enter(self):
        self.ids.SupplierList.open_supplier_list()
        self.ids.SupplierList.open_new_supplier_form()


class CategoryWindow(Screen):
    def on_pre_enter(self):
        self.ids.CategoryList.open_category_list()
        self.ids.CategoryList.open_new_category_form()


class CatalogWindow(Screen):
    def on_pre_enter(self):
        self.ids.ProductList.open_product_list()
        self.ids.ProductList.open_new_product_form()


class AnalyticsWindow(Screen):
    def on_pre_enter(self):
        self.ids.Analytics.open_table(
            "supplier_deliveries", "Кількість доставки від постачальника"
        )
        self.ids.Analytics.open_table(
            "product_sales", "Всі продажи для кожного продукту"
        )


class RegisterCashierWindow(Screen):
    pass


class LoginWindow(Screen):
    pass


class ScanWindow(Screen):
    def on_leave(self):
        try:
            self.ids.CashRegister.stop_cam()
        except Exception:
            print("Can't close camera")


class InvoiceWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


Builder.load_file("MDlog.kv")
Builder.load_file("ProductList.kv")
Builder.load_file("ManufacturerList.kv")
Builder.load_file("SupplierList.kv")
Builder.load_file("CategoryList.kv")
Builder.load_file("InvoiceList.kv")
Builder.load_file("CashRegister.kv")
Builder.load_file("RegisterCashier.kv")
Builder.load_file("Analytics.kv")


class MainApp(MDApp):
    role = ""

    def build(self):
        self.title = "Auto cashier"
        return Builder.load_file("screen_manager.kv")

    def change_screen(self, screan_name: str):
        self.root.current = screan_name

    def connect_to_db(self, username: str, password: str):
        # DRIVER=ODBC Driver 17 for SQL Server;SERVER=GIORNO\SQLEXPRESS;DATABASE=AUTO_CASHIER;
        self.USERNAME = username
        self.PASSWORD = password

        # text cashier
        # self.PASSWORD = "bob"
        # self.USERNAME = "bob"

        # text manager
        self.USERNAME = "nick"
        self.PASSWORD = "0000"
        try:
            file = open("connect.txt", "r")
            connection_string = file.readline()
            file.close()
            self.conn = pyodbc.connect(
                connection_string + f"UID={self.USERNAME};PWD={self.PASSWORD}"
            )
            self.cursor = self.conn.cursor()
            self.set_user_role()
            self.change_screen("main")

        except Exception:
            MDSnackbar(
                MDLabel(
                    text="Неправильне ім'я користувача або пароль",
                ),
            ).open()

    def set_user_role(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"EXEC GET_USER_ROLE '{self.USERNAME}';")
        self.role = self.cursor.fetchone()[0]

    def select_as_dict(self, query: str):
        try:
            self.cursor.execute(query)
            records = []
            columns = [column[0] for column in self.cursor.description]
            records = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            return records
        except Exception as e:
            MDSnackbar(
                MDLabel(
                    text=f"Помилка {e}",
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


if __name__ == "__main__":
    MainApp().run()
