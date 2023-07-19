import time
import math
import sqlite3


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = """SELECT * FROM mainmenu"""
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as ex:
            print(ex)
            print("Ошибка чтения из БД")

        return []

    def addPost(self, title, text):
        try:
            tm = math.floor(time.time())
            self.__cur.execute("""INSERT INTO posts VALUES(NULL, ?, ?, ?)""", (title, text, tm))
            self.__db.commit()
        except sqlite3.Error as ex:
            print(ex, "Ошибка добавления статьи в БД")
            return False
        return True

    def getPost(self, post_id):
        try:
            self.__cur.execute(f""" SELECT title, text FROM posts WHERE id={post_id} LIMIT 1""")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as ex:
            print(ex, "Ошибка чтения из БД")

        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute(f""" SELECT id, title, text FROM posts ORDER BY time DESC""")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as ex:
            print(ex, "Ошибка чтения из БД")

        return []

    def delPost(self, post_id):
        try:
            self.__cur.execute(f'DELETE FROM posts WHERE id={post_id}')
            self.__cur.commit()
        except sqlite3.Error as ex:
            print(ex, "Ошибка БД")

