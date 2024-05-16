from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield.textfield import MDTextField
from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton

import pyodbc


class CategoryList(MDWidget):
    def open_category_list(self):
        if not hasattr(self, "data_tables"):
            products = MDApp.get_running_app().select_as_dict("select * from category;")
            self.data_tables = MDDataTable(
                use_pagination=True,
                size_hint=(1, 0.7),
                column_data=[(col_name, dp(70)) for col_name in products[0].keys()],
                row_data=[(list(pr.values())) for pr in products],
            )
            self.ids.category_list.add_widget(self.data_tables)

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
                INSERT INTO category (category_id, name_category)
                VALUES (?, ?);
            """,
                new_product[0],
                new_product[1],
            )
            MDApp.get_running_app().conn.commit()
            self.data_tables.add_row(new_product)
        except pyodbc.IntegrityError as e:
            MDSnackbar(
                MDLabel(text=f"Invalid data: {e}"),
            ).open()
        except Exception:
            MDSnackbar(
                MDLabel(
                    text="Error, open data table first",
                ),
            ).open()

    def open_new_category_form(self):
        if not hasattr(self, "new_product_form"):
            self.new_product_form = MDBoxLayout(
                orientation="horizontal",
                spacing=5,
                size=(self.width, self.height),
            )
            products = MDApp.get_running_app().select_as_dict("select * from category;")

            for col_name in products[0].keys():
                self.new_product_form.add_widget(
                    MDTextField(required=True, hint_text=col_name, id=col_name)
                )
            self.new_product_form.add_widget(
                MDFlatButton(text="add", on_press=self.add_products)
            )
            self.ids.product_form.add_widget(self.new_product_form)
