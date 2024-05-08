from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.button import Button
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

from pyzbar.pyzbar import decode
from PIL import Image


class MyCamera(MDWidget):
    data = {}
    product_labels = {}
    product_on_screan = {}

    # Camera:
    #     id: camera
    #     resolution: (640, 480)
    #     play: False
    # ToggleButton:
    #     text: 'Play'
    #     on_press: root.toggle_cam()
    def add_product_to_check(self, product_name: str):
        product_info = self.get_product_info(product_name)
        print(product_info)

        if not product_info or product_info[3] <= 1:
            MDSnackbar(
                MDLabel(
                    text="Product in check or there no such product",
                ),
            ).open()
            return

        sku = product_info[0]
        product_name = product_info[1]
        price = product_info[2]
        quantity_in_stock = product_info[3]

        self.ids.selected_product.text = f"{product_name}, price: {price}"
        self.data[product_name] = {
            "quantity_in_check": 1,
            "quantity_in_stock": quantity_in_stock,
            "price": price,
            "sku": sku,
        }
        check_item = MDBoxLayout(size_hint_y=None)
        check_item.add_widget(MDLabel(text=f"{product_info[1]}"))
        label = MDLabel(
            id=product_name, text=f"{self.data[product_name]['quantity_in_check']}"
        )
        self.product_labels[product_name] = label

        check_item.add_widget(label)

        def on_press_function(product, callback):
            return lambda x: callback(product)

        check_item.add_widget(
            Button(
                text="+",
                on_press=on_press_function(product_name, self.increment_product),
            )
        )
        check_item.add_widget(
            Button(
                text="-",
                on_press=on_press_function(product_name, self.decrement_product),
            )
        )
        self.product_on_screan[product_name] = check_item

        self.ids.product_list.add_widget(check_item)

    def cancel(self):
        for _, wdg in self.product_on_screan.items():
            self.ids.product_list.remove_widget(wdg)
        self.product_on_screan = {}
        self.product_labels = {}
        self.data = {}

    def increment_product(self, product: str):
        if product in self.data:
            if (
                self.data[product]["quantity_in_check"]
                < self.data[product]["quantity_in_stock"]
            ):
                self.data[product]["quantity_in_check"] += 1
                self.product_labels[product].text = str(
                    self.data[product]["quantity_in_check"]
                )
            else:
                MDSnackbar(
                    MDLabel(
                        text="Not enoght product in stock",
                    ),
                ).open()

    def decrement_product(self, product: str):
        if product in self.data:
            self.data[product]["quantity_in_check"] -= 1
            self.product_labels[product].text = str(
                self.data[product]["quantity_in_check"]
            )
            if self.data[product]["quantity_in_check"] <= 0:
                self.ids.product_list.remove_widget(self.product_on_screan[product])
                del self.data[product]

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
                    self.add_product_to_check(decoded)

    def get_product_info(self, sku: str):
        cursor = MDApp.get_running_app().cursor
        query = """SELECT product.SKU, product.product_name, product_in_stock.price, product_in_stock.quantity_in_stock
                    FROM product_in_stock
                    JOIN product ON product_in_stock.SKU = product.SKU
                    WHERE product.SKU = ? OR product.product_name = ?;"""
        cursor.execute(query, sku, sku)
        result = cursor.fetchone()
        if result and result[1] in self.data.keys():
            return None
        return result

    # TODO:
    def get_check(self):
        pass
