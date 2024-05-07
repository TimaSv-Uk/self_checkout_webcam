from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.widget import MDWidget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.datatables import MDDataTable
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivymd.uix.label import MDLabel
from kivy.uix.anchorlayout import AnchorLayout
from kivy.metrics import dp
from kivy.lang import Builder

from pyzbar.pyzbar import decode
from PIL import Image

import pyodbc


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
        else:
            self.ids.app_bar.right_action_items = []

    def open_screan(self, screan_name):
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


class MyCamera(MDWidget):
    data = {"cup": 12, "coffy": 2}
    product_labels = {}
    product_on_screan = {}

    # Camera:
    #     id: camera
    #     resolution: (640, 480)
    #     play: False
    # ToggleButton:
    #     text: 'Play'
    #     on_press: root.toggle_cam()
    def press(self):
        for product, quantity in self.data.items():
            if product in self.product_labels or product in self.product_on_screan:
                continue

            check_item = BoxLayout(size_hint_y=None)
            check_item.add_widget(MDLabel(text=f"{product}"))
            label = MDLabel(id=product, text=f"{quantity}")
            self.product_labels[product] = label

            check_item.add_widget(label)

            def on_press_function(product, callback):
                return lambda x: callback(product)

            check_item.add_widget(
                Button(
                    text="+",
                    on_press=on_press_function(product, self.increment_product),
                )
            )
            check_item.add_widget(
                Button(
                    text="-",
                    on_press=on_press_function(product, self.decrement_product),
                )
            )
            self.product_on_screan[product] = check_item

            self.ids.product_list.add_widget(check_item)

    def cancel(self):
        for _, wdg in self.product_on_screan.items():
            self.ids.product_list.remove_widget(wdg)
        self.product_on_screan = {}
        self.product_labels = {}

    def increment_product(self, product):
        if product in self.data:
            self.data[product] += 1
            self.product_labels[product].text = str(self.data[product])

    def decrement_product(self, product):
        if product in self.data:
            self.data[product] -= 1
            if self.data[product] <= 0:
                self.ids.product_list.remove_widget(self.product_on_screan[product])

            self.product_labels[product].text = str(self.data[product])

    def toggle_cam(self):
        self.ids.camera.play = not self.ids.camera.play
        if self.ids.camera.play:
            Clock.schedule_interval(self.scan_qr, 1 / 100.0)  # scan at 30 FPS
        else:
            Clock.unschedule(self.scan_qr)

    def stop_cam(self):
        self.ids.camera.play = False

    def scan_qr(self, dt):
        # get the current frame from the camera
        frame = self.ids.camera.texture
        if frame is not None:
            # convert the frame to an image
            size = frame.width, frame.height
            img = Image.frombytes("RGBA", size, frame.pixels)
            img = img.convert("L")  # convert to grayscale

            # scan the image for QR codes
            codes = decode(img)
            for code in codes:
                decoded = code.data.decode("utf-8")
                if decoded not in self.data:
                    self.data[decoded] = 1
                    self.ids.selected_product.text = decoded
                    self.press()


class MyMDLog(MDWidget):
    def login(self):
        MDApp.get_running_app().connect_to_db(
            self.ids.user.text, self.ids.password.text
        )

    def clear(self):
        connection = MDApp.get_running_app().cursor
        try:
            connection.execute("select * from invoice;")
            for row in connection.fetchall():
                print(row)
        except pyodbc.ProgrammingError as e:
            print("Permission was denied:", e)

        try:
            connection.execute("select * from product;")
            for row in connection.fetchall():
                print(row)
        except pyodbc.ProgrammingError as e:
            print("Permission was denied:", e)
        self.ids.user.text = ""
        self.ids.password.text = ""


Builder.load_file("MDlog.kv")
Builder.load_file("camera.kv")


class MainApp(MDApp):
    role = ""

    def build(self):
        return Builder.load_file("screen_manager.kv")

    def change_screen(self, screan_name):
        self.root.current = screan_name

    def connect_to_db(self, username, password):
        # self.USERNAME = username
        # self.PASSWORD = password
        self.USERNAME = "bob"
        self.PASSWORD = "bob"
        try:
            file = open("connect.txt", "r")
            connection_string = file.readline()
            self.conn = pyodbc.connect(
                connection_string + f"UID={self.USERNAME};PWD={self.PASSWORD}"
            )
            self.cursor = self.conn.cursor()
            self.set_user_role()
            # self.change_screen("main")
        except:
            MDSnackbar(
                MDLabel(
                    text="Invalid user name or password",
                ),
            ).open()

    def set_user_role(self):
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"EXEC GET_USER_ROLE '{self.USERNAME}';")
        self.role = self.cursor.fetchone()[0]


MainApp().run()
