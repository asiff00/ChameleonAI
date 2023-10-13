# man.py
import os
import sys
import shutil
from PIL import Image
from ui import ChatbotApp


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
    print("Base path ", base_path)
    return os.path.join(base_path, relative_path)


def main():
    
    
    bundle_data_path = resource_path('src/data/database.json')
    icon = Image.open(resource_path("img/ChameleonAI.jpeg"))
    persistent_data_path = os.path.join(os.getenv('APPDATA'), 'ChameleonAI/src/data/database.json')
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.makedirs(os.path.dirname(persistent_data_path), exist_ok=True)
        if not os.path.isfile(persistent_data_path):
            shutil.copyfile(bundle_data_path, persistent_data_path)
    else:
        persistent_data_path=bundle_data_path
    app = ChatbotApp(persistent_data_path, icon)
    app.run()


if __name__ == "__main__":
    main()
