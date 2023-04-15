import sqlite3


class Database:

    def __init__(self, file_db):
        self.connection = sqlite3.connect(file_db)
        self.cursor = self.connection.cursor()

    def add_link(self, user_id, link):
        with self.connection:
            self.cursor.execute("INSERT INTO links (user_id, link) VALUES (?, ?)", (user_id, link))

    def get_links(self):
        with self.connection:
            return self.cursor.execute("SELECT user_id, link, state FROM links").fetchall()

    def update_state_link(self, link, state):
        with self.connection:
            self.cursor.execute("UPDATE links SET state = ? WHERE link = ?", (state, link))

    def get_links_by_user(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM links WHERE user_id = ?", (user_id, )).fetchall()

    def delete_all_links(self, user_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM links WHERE user_id = ?", (user_id, ))