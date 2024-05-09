from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar

class RegisterCashier(MDWidget):
    def register_cashier(self):

        try:
            MDApp.get_running_app().cursor.execute(
                """
                EXEC AddCashier ?, ?;
                """,
                self.ids.user.text,
                self.ids.password.text,
            )
            MDApp.get_running_app().conn.commit()

            MDSnackbar(
                MDLabel(
                    text=f"Cashier {self.ids.user.text} was hired",
                ),
            ).open()
        except Exception as e:
            MDSnackbar(
                MDLabel(
                    text=f"Duplicate cashier name: {e}",
                ),
            ).open()

    def delete_cashier(self):
        try:
            MDApp.get_running_app().cursor.execute(
                """
                EXEC DeleteCashier ?;
                """,
                self.ids.remove_user_name.text,
            )
            MDApp.get_running_app().conn.commit()

            MDSnackbar(
                MDLabel(
                    text=f"Cashier {self.ids.remove_user_name.text} was fired",
                ),
            ).open()
        except Exception:
            MDSnackbar(
                MDLabel(
                    text="Cashier not found",
                ),
            ).open()

    def clear_add(self):
        self.ids.user.text = ""
        self.ids.password.text = ""

    def clear_delete(self):
        self.ids.remove_user_name.text = ""
