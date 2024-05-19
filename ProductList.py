from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield.textfield import MDTextField
from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatButton

import pyodbc
import qrcode


class ProductList(MDWidget):
    def open_product_list(self):
        if not hasattr(self, "data_tables"):
            products = MDApp.get_running_app().select_as_dict("select * from product;")
            self.data_tables = MDDataTable(
                use_pagination=True,
                size_hint=(1, 0.7),
                column_data=[(col_name, dp(70)) for col_name in products[0].keys()],
                row_data=[(list(pr.values())) for pr in products],
            )
            self.data_tables.bind(on_row_press=self.get_qr_code)
            self.ids.product_list.add_widget(self.data_tables)

    def add_products(self, *args):
        try:
            new_product = [
                widget.text
                for widget in self.new_product_form.children
                if isinstance(widget, MDTextField)
            ]
            new_product = list(reversed(new_product))
            MDApp.get_running_app().cursor.execute(
                """
                INSERT INTO product (SKU, product_name, id_category, id_manufacturer, product_description)
                VALUES (?, ?, ?,
                        ?, ?);
            """,
                new_product[0],
                new_product[1],
                new_product[2],
                new_product[3],
                new_product[4],
            )
            MDApp.get_running_app().conn.commit()
            self.data_tables.add_row(new_product)
        except pyodbc.IntegrityError as e:
            MDSnackbar(
                MDLabel(text=f"Неправильні дані: {e}"),
            ).open()
        except Exception:
            MDSnackbar(
                MDLabel(
                    text="Помилка, спочатку відкрийте таблицю даних",
                ),
            ).open()

    def open_new_product_form(self):
        if not hasattr(self, "new_product_form"):
            self.new_product_form = MDBoxLayout(
                orientation="horizontal",
                spacing=5,
                size=(self.width, self.height * 0.9),
            )
            products = MDApp.get_running_app().select_as_dict("select * from product;")

            for col_name in products[0].keys():
                self.new_product_form.add_widget(
                    MDTextField(required=True, hint_text=col_name, id=col_name)
                )
            self.new_product_form.add_widget(
                MDFillRoundFlatButton(text="add", on_press=self.add_products)
            )
            self.ids.product_form.add_widget(self.new_product_form)

    def get_qr_code(self, instance_table, instance_row):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # SKU is first row
        if instance_row.index % 5 == 0:
            qr.add_data(instance_row.text)

            qr_image = qr.make_image()
            qr_image.show()
