from kivy.clock import Clock
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.widget import MDWidget
from kivymd.uix.textfield import MDTextField
from PIL import Image
from pyzbar.pyzbar import decode
import random
import string
import datetime


class InvoiceList(MDWidget):
    data = {}
    invoice_on_screan = {}

    def add_invoice_line(self, product_name: str):
        invoice_info = self.get_product_info(product_name)
        if not invoice_info:
            MDSnackbar(
                MDLabel(
                    text="No such product in product list",
                ),
            ).open()
            return

        sku = invoice_info[0]

        self.data[product_name] = {
            "quantity_delivered": 1,
            "sku": sku,
        }
        check_item = MDBoxLayout(size_hint_y=None)
        check_item.add_widget(MDLabel(id="product_name", text=f"{product_name}"))

        check_item.add_widget(
            MDTextField(id="supplier_id", hint_text="supplier id", max_text_length=3)
        )
        check_item.add_widget(
            MDTextField(
                id="measurement_unit", hint_text="measurement unit", max_text_length=10
            )
        )
        check_item.add_widget(
            MDTextField(
                id="delivery_price", hint_text="delivery price", input_filter="float"
            )
        )
        check_item.add_widget(
            MDTextField(
                id="quantity_delivered",
                hint_text="Quantity",
                input_filter="int",
            )
        )
        self.invoice_on_screan[product_name] = check_item

        self.ids.invoice_list.add_widget(check_item)

    def cancel(self):
        self.get_unique_invoice_id()
        for _, wdg in self.invoice_on_screan.items():
            self.ids.invoice_list.remove_widget(wdg)
        self.invoice_on_screan = {}
        self.invoice_labels = {}
        self.data = {}

    def add_invoice(self):
        if len(self.data) > 0:
            invoice_id = self.get_unique_invoice_id()
            MDApp.get_running_app().cursor.execute(
                """
                INSERT INTO invoice (invoice_id, delivery_date ,delivery_time)
                VALUES (?, ?, ?);
                """,
                invoice_id,
                datetime.date.today(),
                datetime.datetime.now().time(),
            )
            MDApp.get_running_app().conn.commit()
            for index, invoice_name in enumerate(self.invoice_on_screan):
                for child in self.invoice_on_screan[invoice_name].children:
                    if isinstance(child, MDTextField):
                        widget_id = child.id
                        text = child.text
                        self.data[invoice_name][widget_id] = text
                try:
                    MDApp.get_running_app().cursor.execute(
                        """
                        INSERT INTO invoice_line (SKU, delivery_price, 
                            line_number, supplier_id, measurement_unit,quantity_delivered, invoice_id)
                        VALUES (?, ?, ?, ?, ?, ?,?);
                        """,
                        self.data[invoice_name]["sku"],
                        self.data[invoice_name]["delivery_price"],
                        index + 1,
                        self.data[invoice_name]["supplier_id"],
                        self.data[invoice_name]["measurement_unit"],
                        self.data[invoice_name]["quantity_delivered"],
                        invoice_id,
                    )
                    MDApp.get_running_app().conn.commit()
                except Exception as e:
                    print(e)
                    MDSnackbar(
                        MDLabel(
                            text=f"Invalid input {e}",
                        ),
                    ).open()
                    return
            self.cancel()
            MDSnackbar(
                MDLabel(
                    text=f"Invoice with id {invoice_id} was added",
                ),
            ).open()

    def get_unique_invoice_id(self):
        check_ids = MDApp.get_running_app().cursor.execute(
            "select invoice_id from invoice;"
        )
        check_ids = [id[0] for id in check_ids.fetchall()]
        unique_string = "".join(
            random.choices(string.ascii_letters + string.digits, k=9)
        )
        while True:
            if unique_string not in check_ids:
                break
            unique_string = "".join(
                random.choices(string.ascii_letters + string.digits, k=15)
            )
        return unique_string

    def get_product_info(self, sku: str):
        cursor = MDApp.get_running_app().cursor
        query = """SELECT product.SKU, product.product_name
                    FROM product
                    WHERE product.SKU = ? OR product.product_name = ?;"""
        cursor.execute(query, sku, sku)
        result = cursor.fetchone()
        if result and result[1] in self.data.keys():
            return None
        return result
