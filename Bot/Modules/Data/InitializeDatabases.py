import peewee
from peewee import SqliteDatabase

from Bot.Modules.Data.cortemundial import Profiles, Messages


class InitializeDatabases:
    def __init__(self, console):
        self.console = console


    def initializeCorte(self):
        db = SqliteDatabase("Data/users.db")
        try:
            db.connect()
        except peewee.OperationalError as e:
            # If the connection is already open, ignore the exception
            if 'Connection already opened' not in str(e):
                self.console.log(f"[ERROR] {e}")

        db_list = [Profiles, Messages]
        db.create_tables([item for item in db_list], safe=True)
