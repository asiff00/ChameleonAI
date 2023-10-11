# brain.py
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
            return None

    def initialize(self, context, temperature=0.7):
        try:
            self.response = None
            prompt = (
                "Your character is as follows: "
                + context
                + ". From now on, you’ll role play as the described character. Your first reply should be a one-line introduction based on the provided character, starting with ‘I am’."
            )
            self.response = palm.chat(context=context, messages=prompt)
            return self.response.last
        except:
            return "No API Found - Please set up a valid API first."

    @retry.Retry()
    def generate_text(self, prompt, temperature=0.7):
        try:
            return (
                "I'd rather not answer"
                if self.response.reply(prompt).last is None
                else self.response.reply(prompt).last
            )
        except:
            return "Error - Invalid API or connectivity issue: Please check your API credentials or internet connection"
