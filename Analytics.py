from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.textfield.textfield import MDTextField
from kivy.metrics import dp
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton

import pyodbc


class Analytics(MDWidget):
    data_tables = {}
    data_tables_label = {}

    def open_table(self, table_name: str, description: str):
        if table_name not in self.data_tables.keys():
            products = MDApp.get_running_app().select_as_dict(
                f"select * from {table_name};"
            )
            self.data_tables[table_name] = MDDataTable(
                use_pagination=True,
                size_hint=(1, 0.7),
                column_data=[(col_name, dp(70)) for col_name in products[0].keys()],
                row_data=[(list(pr.values())) for pr in products],
            )
            self.data_tables_label[table_name] = MDLabel(
                text=description,
                size_hint_y=None,
                size=(200, 40),
                font_style="H6",
            )

            self.ids.analytics_layout.add_widget(self.data_tables_label[table_name])
            self.ids.analytics_layout.add_widget(self.data_tables[table_name])
        else:
            self.ids.analytics_layout.remove_widget(self.data_tables_label[table_name])
            self.ids.analytics_layout.remove_widget(self.data_tables[table_name])
            products = MDApp.get_running_app().select_as_dict(
                f"select * from {table_name};"
            )
            self.data_tables[table_name] = MDDataTable(
                use_pagination=True,
                size_hint=(1, 0.7),
                column_data=[(col_name, dp(70)) for col_name in products[0].keys()],
                row_data=[(list(pr.values())) for pr in products],
            )

            self.ids.analytics_layout.add_widget(self.data_tables_label[table_name])
            self.ids.analytics_layout.add_widget(self.data_tables[table_name])
