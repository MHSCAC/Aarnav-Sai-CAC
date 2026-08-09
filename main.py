import pyttsx3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.window import Window

# Set dark background to match design
Window.clearcolor = (0.07, 0.07, 0.07, 1)

class ListenLinkApp(App):
    def build(self):
        # Initialize Text-to-Speech Engine
        self.tts_engine = pyttsx3.init()

        # Root Layout
        root = BoxLayout(orientation='vertical', padding=30, spacing=20)

        # 1. Continuous Live Captions Label
        self.caption_label = Label(
            text="Hi! Can you point me towards the main office?",
            font_size='28sp',
            color=(0.99, 0.98, 0.96, 1),
            text_size=(Window.width - 60, None),
            halign='left',
            valign='middle',
            size_hint=(1, 0.8)
        )
        root.add_widget(self.caption_label)

        # 2. Reply Action Button
        reply_btn = Button(
            text="Reply",
            font_size='22sp',
            background_color=(0.17, 0.51, 0.96, 1),
            background_normal='',
            size_hint=(1, 0.15),
            border=(10, 10, 10, 10)
        )
        reply_btn.bind(on_press=self.open_reply_popup)
        root.add_widget(reply_btn)

        return root

    def open_reply_popup(self, instance):
        # Popup container for speech response
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.text_input = TextInput(
            hint_text="Type your response...",
            font_size='20sp',
            multiline=True,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            size_hint=(1, 0.7)
        )
        content.add_widget(self.text_input)

        send_btn = Button(
            text="Send & Speak",
            font_size='18sp',
            background_color=(0.17, 0.51, 0.96, 1),
            background_normal='',
            size_hint=(1, 0.3)
        )
        
        popup = Popup(
            title="Type Response",
            content=content,
            size_hint=(0.9, 0.5),
            auto_dismiss=True
        )
        
        send_btn.bind(on_press=lambda x: self.speak_and_close(popup))
        content.add_widget(send_btn)
        popup.open()

    def speak_and_close(self, popup):
        message = self.text_input.text.strip()
        if message:
            # Speak typed message out loud
            self.tts_engine.say(message)
            self.tts_engine.runAndWait()
        popup.dismiss()

if __name__ == '__main__':
    ListenLinkApp().run()