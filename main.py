from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
import requests

# Configure window size for development
Window.size = (360, 640)

class SignUpPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Sign Up"
        self.size_hint = (0.8, 0.8)

        layout = BoxLayout(orientation='vertical')

        self.first_name = TextInput(hint_text="First Name", multiline=False)
        self.last_name = TextInput(hint_text="Last Name", multiline=False)
        self.email = TextInput(hint_text="Email", multiline=False)
        self.password = TextInput(hint_text="Password", multiline=False, password=True)
        self.confirm_password = TextInput(hint_text="Confirm Password", multiline=False, password=True)

        submit_button = Button(text="Submit")
        submit_button.bind(on_press=self.submit)

        layout.add_widget(self.first_name)
        layout.add_widget(self.last_name)
        layout.add_widget(self.email)
        layout.add_widget(self.password)
        layout.add_widget(self.confirm_password)
        layout.add_widget(submit_button)

        self.content = layout

    def submit(self, instance):
        if self.password.text != self.confirm_password.text:
            popup = Popup(title="Error", content=Label(text="Passwords do not match"), size_hint=(0.8, 0.4))
            popup.open()
        else:
            # Handle the sign-up process with the Flask backend
            data = {
                'first_name': self.first_name.text,
                'last_name': self.last_name.text,
                'email': self.email.text,
                'password': self.password.text
            }
            response = requests.post('http://127.0.0.1:5000/signup', json=data)
            if response.status_code == 200:
                self.dismiss()
            else:
                popup = Popup(title="Error", content=Label(text="Sign-up failed"), size_hint=(0.8, 0.4))
                popup.open()

class LoginPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Log In"
        self.size_hint = (0.8, 0.8)

        layout = BoxLayout(orientation='vertical')

        self.email = TextInput(hint_text="Email", multiline=False)
        self.password = TextInput(hint_text="Password", multiline=False, password=True)

        login_button = Button(text="Log In")
        login_button.bind(on_press=self.login)

        layout.add_widget(self.email)
        layout.add_widget(self.password)
        layout.add_widget(login_button)

        self.content = layout

    def login(self, instance):
        # Handle the login process with the Flask backend
        data = {
            'email': self.email.text,
            'password': self.password.text
        }
        response = requests.post('http://127.0.0.1:5000/login', json=data)
        if response.status_code == 200:
            self.dismiss()
        else:
            popup = Popup(title="Error", content=Label(text="Log-in failed"), size_hint=(0.8, 0.4))
            popup.open()

class UploadPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Upload Document"
        self.size_hint = (0.8, 0.8)

        layout = BoxLayout(orientation='vertical')
        self.filechooser = FileChooserListView()
        layout.add_widget(self.filechooser)

        upload_button = Button(text="Upload")
        upload_button.bind(on_press=self.upload)

        layout.add_widget(upload_button)
        self.content = layout

    def upload(self, instance):
        selected = self.filechooser.selection
        if selected:
            # Handle the file upload process with the Flask backend
            file_path = selected[0]
            files = {'file': open(file_path, 'rb')}
            response = requests.post('http://127.0.0.1:5000/upload', files=files)
            if response.status_code == 200:
                self.dismiss()
            else:
                popup = Popup(title="Error", content=Label(text="Upload failed"), size_hint=(0.8, 0.4))
                popup.open()

class MainApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        sign_up_button = Button(text="Sign Up")
        sign_up_button.bind(on_press=self.open_sign_up_popup)

        log_in_button = Button(text="Log In")
        log_in_button.bind(on_press=self.open_log_in_popup)

        upload_button = Button(text="Upload Document")
        upload_button.bind(on_press=self.open_upload_popup)

        subscribe_button = Button(text="Subscribe")
        subscribe_button.bind(on_press=self.subscribe)

        layout.add_widget(sign_up_button)
        layout.add_widget(log_in_button)
        layout.add_widget(upload_button)
        layout.add_widget(subscribe_button)

        return layout

    def open_sign_up_popup(self, instance):
        popup = SignUpPopup()
        popup.open()

    def open_log_in_popup(self, instance):
        popup = LoginPopup()
        popup.open()

    def open_upload_popup(self, instance):
        popup = UploadPopup()
        popup.open()

    def subscribe(self, instance):
        # Handle the subscription process
        popup = Popup(title="Subscription", content=Label(text="Subscription process"), size_hint=(0.8, 0.4))
        popup.open()

if __name__ == '__main__':
    MainApp().run()