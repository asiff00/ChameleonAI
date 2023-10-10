import google.generativeai as palm
from google.api_core import retry

class ChatbotBackend:
    def __init__(self, palm_api_key):
        self.palm_api_key = palm_api_key
        self.configure_palm()
        self.response = None

    def configure_palm(self):
        try:
            palm.configure(api_key=self.palm_api_key)
        except:
            self.hasAPI = False

    def initialize(self, context, prompt, temperature=0.7):
        try:
            self.response = palm.chat(context=context, messages=prompt)
            return self.response.last
        except:
            return "No API Found - Please set up a valid API first."

    @retry.Retry()
    def generate_text(self, prompt, temperature=0.7):
        try:
            return "Sorry, could you please rephrase it?" if self.response.reply(prompt).last is None else self.response.reply(prompt).last
        except:
            return "Error - Invalid API or connectivity issue: Please check your API credentials or internet connection"