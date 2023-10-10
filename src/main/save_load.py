#save_load.py
import json
class Database:
    def __init__(self, database):
        self.data = database
        self.load()

    def load(self):
        try:
            with open(self.data, "r") as data:
                self.database = json.load(data)
        except FileNotFoundError:
            self.database = {"api": "", "priming": "", "decorator": ""}

    def save(self):
        with open(self.data, "w") as data:
            json.dump(self.database, data)

    def set_api(self, value):
        self.database["api"] = value
        self.save()

    def set_priming(self, value):
        self.database["priming"] = value
        self.save()

    def set_decorator(self, value):
        self.database["decorator"] = value
        self.save()

    def get_api(self):
        return self.database["api"]

    def get_priming(self):
        return self.database["priming"]

    def get_decorator(self):
        return self.database["decorator"]
