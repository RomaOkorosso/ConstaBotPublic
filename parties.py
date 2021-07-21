import database_functions
import config
import datetime

con = config.connect_with_database()


class GameCharacter:
    def __init__(self, id, username, hp, full_hp, st, en, next_en):
        self.id = id
        self.username = username
        self.hp = hp
        self.full_hp = full_hp
        self.st = st
        self.en = en
        self.next_en = next_en

    def get_next_en_from_db(self):
        cur = con.cursor()
        cur.execute(f"""SELECT next_en FROM parties WHERE user_id = {self.id}""")
        next_en = cur.fetchone()
        self.next_en = next_en

    def get_username_from_txt(self, txt: str, num_in_txt: int):
        left = txt.find(f"{num_in_txt})")
        left = txt.find("[", left)
        right = txt.find("\n", left)
        self.username = txt[left : txt.find("🏅", left, right)]


class Party:
    def __init__(
        self,
    ):
        pass
