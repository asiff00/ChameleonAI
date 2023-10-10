import google.generativeai as palm
from google.api_core import retry

class ChatbotBackend:
    def __init__(self, palm_api_key):
        self.palm_api_key = palm_api_key
        self.configure_palm()
        self.response = None
        self.model = True

    def configure_palm(self):
        try:
            palm.configure(api_key=self.palm_api_key)

        except:
            print(f"INVALID API KEY: {self.palm_api_key}")
            self.model = None

    def initialize(self, context, prompt, temperature=0.7):
        try:
            if self.model is None:
                return "NO API FOUND: Set up API first."
            self.response = palm.chat(context=context, messages=prompt)
            return self.response.last
        except:
            return "Error: Check your internet connection"

    @retry.Retry()
    def generate_text(self, prompt, temperature=0.5):
        try:
            if self.model is None:
                return "NO API FOUND: Set up API first."
            return "Sorry, could you please rephrase it?" if self.response.reply(prompt).last is None else self.response.reply(prompt).last
        except:
            return "Error: Check your internet connection"