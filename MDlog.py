from kivymd.app import MDApp
from kivymd.uix.widget import MDWidget


class MyMDLog(MDWidget):
    def login(self):
        MDApp.get_running_app().connect_to_db(
            self.ids.user.text, self.ids.password.text
        )

    def clear(self):
        self.ids.user.text = ""
        self.ids.password.text = ""
