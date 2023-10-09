# main.py
from ui import ChatbotApp
import os
from dotenv import load_dotenv 


def main():
    load_dotenv()
    palm_api_key = os.getenv('API_KEY')
    app = ChatbotApp(palm_api_key)
    app.run()
    
if __name__ == "__main__":
    main()
