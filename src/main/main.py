import os
import sys
from dotenv import load_dotenv
from ui import ChatbotApp

def main():
    load_dotenv()
    path = os.getenv("ROOT_DIR")
    print(path)
    app = ChatbotApp(str(path) + "\src\data\database.json")
    app.run()
    
if __name__ == "__main__":
    main()
