import google.generativeai as palm
from google.api_core import retry


class ChatbotBackend:
    def __init__(self, palm_api_key):
        self.palm_api_key = palm_api_key
        self.configure_palm()
        self.response = None

    def configure_palm(self):
        palm.configure(api_key=self.palm_api_key)
        models = [m for m in palm.list_models()
                  if 'generateText' in m.supported_generation_methods]
        self.model = models[0]

    def initialize(self, context, prompt, temperature=0.1):
        self.response = None
        self.response = palm.chat(context=context, messages=prompt)
        return self.response.last

    @retry.Retry()
    def generate_text(self, prompt, temperature=0.3):
        return self.response.reply(prompt).last
