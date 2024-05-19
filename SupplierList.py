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


class SupplierList(MDWidget):
    def open_supplier_list(self):
        if not hasattr(self, "data_tables"):
            products = MDApp.get_running_app().select_as_dict("select * from supplier;")
            self.data_tables = MDDataTable(
                use_pagination=True,
                size_hint=(1, 0.7),
                column_data=[(col_name, dp(70)) for col_name in products[0].keys()],
                row_data=[(list(pr.values())) for pr in products],
            )
            self.ids.supplier_list.add_widget(self.data_tables)

    def add_products(self, *args):
        try:
            new_product = [
                widget.text
                for widget in self.new_supplier_form.children
                if isinstance(widget, MDTextField)
            ]
            new_product = list(reversed(new_product))
            MDApp.get_running_app().cursor.execute(
                """
                INSERT INTO supplier (supplier_id, name_supplier)
                VALUES (?, ?);
            """,
                new_product[0],
                new_product[1],
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

    def open_new_supplier_form(self):
        if not hasattr(self, "new_supplier_form"):
            self.new_supplier_form = MDBoxLayout(
                orientation="horizontal",
                spacing=5,
                size=(self.width, self.height),
            )
            products = MDApp.get_running_app().select_as_dict("select * from supplier;")

            for col_name in products[0].keys():
                self.new_supplier_form.add_widget(
                    MDTextField(required=True, hint_text=col_name, id=col_name)
                )
            self.new_supplier_form.add_widget(
                MDFillRoundFlatButton(text="додати", on_press=self.add_products)
            )
            self.ids.product_form.add_widget(self.new_supplier_form)
