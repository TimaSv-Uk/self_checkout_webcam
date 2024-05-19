from kivy.clock import Clock
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.widget import MDWidget
from PIL import Image
from pyzbar.pyzbar import decode
import random
import string
import datetime


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os


class CashRegister(MDWidget):
    data = {}
    product_labels = {}
    product_on_screan = {}

    def add_product_to_check(self, product_name: str):
        product_info = self.get_product_info(product_name)

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
        self.get_unique_check_id()
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
        frame = self.ids.camera.texture
        if frame is not None:
            size = frame.width, frame.height
            img = Image.frombytes("RGBA", size, frame.pixels)
            img = img.convert("L")
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

    def get_check(self):
        if len(self.data) > 0:
            check_id = self.get_unique_check_id()
            MDApp.get_running_app().cursor.execute(
                """
                INSERT INTO final_сheck (сheck_id, sale_date ,sale_time)
                VALUES (?, ?, ?);
                """,
                check_id,
                datetime.date.today(),
                datetime.datetime.now().time(),
            )
            MDApp.get_running_app().conn.commit()
            for index, product_name in enumerate(self.data):
                MDApp.get_running_app().cursor.execute(
                    """
                    INSERT INTO check_line (SKU, quantity_sold, line_number, check_id)
                    VALUES (?, ?, ?, ?);
                    """,
                    self.data[product_name]["sku"],
                    self.data[product_name]["quantity_in_check"],
                    index + 1,
                    check_id,
                )
                MDApp.get_running_app().conn.commit()
            self.create_pdf(check_id)
            self.cancel()

    def get_unique_check_id(self):
        check_ids = MDApp.get_running_app().cursor.execute(
            "select сheck_id from final_сheck;"
        )
        check_ids = [id[0] for id in check_ids.fetchall()]
        unique_string = "".join(
            random.choices(string.ascii_letters + string.digits, k=15)
        )
        while True:
            if unique_string not in check_ids:
                break
            unique_string = "".join(
                random.choices(string.ascii_letters + string.digits, k=15)
            )
        return unique_string

    def create_pdf(self, check_id):
        c = canvas.Canvas("check.pdf", pagesize=letter)
        width, height = letter

        data = (
            MDApp.get_running_app()
            .cursor.execute(
                "select * from dbo.check_with_line_products where check_id = ? order by line_number;",
                check_id,
            )
            .fetchall()
        )
        c.setFont("Helvetica-Bold", 18)
        c.drawString(30, height - 50, "Check")
        c.setFont("Helvetica", 12)

        c.drawString(30, height - 80, "Quantity Sold")
        c.drawString(130, height - 80, "Product Name")
        c.drawString(230, height - 80, "Price for one")
        c.drawString(330, height - 80, "Price for quantity")
        y = height - 100

        total_price = 0
        for row in data:
            (
                check_id,
                sale_date,
                sale_time,
                line_number,
                quantity_sold,
                sku,
                product_name,
                price,
                total_line_price,
            ) = row
            c.drawString(30, y, str(quantity_sold))
            c.drawString(130, y, str(product_name))
            c.drawString(230, y, str(price))
            c.drawString(330, y, str(total_line_price))
            y = y - 20
            total_price += total_line_price

        c.setFont("Helvetica-Bold", 14)
        c.drawString(
            30,
            y - 40,
            f"Check ID: {check_id}, Sale Date: {sale_date}, Sale Time: {sale_time}",
        )
        c.drawString(
            30,
            y - 60,
            f"Total price: {total_price}",
        )

        c.save()
        os.startfile("check.pdf")
        return
