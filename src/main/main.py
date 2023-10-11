#man.py
import os
import sys
from ui import ChatbotApp

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    print(base_path)
    return os.path.join(base_path, relative_path)

def main():
    path = resource_path('src\data\database.json')
    app = ChatbotApp(path)
    app.run()
    
if __name__ == "__main__":
    main()
