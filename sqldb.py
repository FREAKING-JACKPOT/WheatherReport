import sqlite3


class sqldb:
    def __init__(self, db_file):
        """Подключение к БД и сохраняем курсор"""
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
