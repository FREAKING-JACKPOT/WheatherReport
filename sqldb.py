import sqlite3


class db:
    def __init__(self, db_file):
        """Подключение к БД и сохраняем курсор"""
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def get_subs(self, status=True):
        '''Получаем всех сабов'''
        with self.connection:
            return self.cursor.execute(
                "SELECT * FROM `subs` WHERE `status` = ?",
                (status, )).fetchall()

    def sub_exists(self, user_id):
        ''' Проверяем есть ли саб в БД'''
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM `subs` WHERE `user_id` = ?",
                (user_id, )).fetchall()
            return bool(len(result))

    def add_sub(self, user_id, City, status=True):
        ''' Добавим в БД саба'''
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO `subs` (`user_id`, `status`, `City`) VALUES (?,?,?)",
                (user_id, status, City))

    def update_sub(self, user_id, city_id):
        """Обновление города подписки"""
        with self.connection:
            return self.cursor.execute(
                "UPDATE subs SET City = ? WHERE `user_id` = ?",
                (city_id, user_id))

    def delete_sub(self, user_id):
        """Удаление подписки"""
        with self.connection:
            return self.cursor.execute("DELETE FROM subs WHERE user_id = ?",
                                       (user_id, ))

    def close(self):
        '''Отключение соединения от БД '''
        self.connection.close()