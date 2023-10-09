# main.py
from ui import ChatbotApp

def main():
    app = ChatbotApp('database.json')
    app.run()
    
if __name__ == "__main__":
    main()
