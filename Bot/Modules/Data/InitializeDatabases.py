import peewee
from peewee import SqliteDatabase

from Bot.Data.cortemundial import Profiles, Messages


class InitializeDatabases:
    def __init__(self, console, directory):
        self.console = console
        self.directory = directory


    def initializeCorte(self):
        db_file = self.directory / 'Data' / 'corte.db'
        self.console.log(f"Resolved path {db_file}")
        db = SqliteDatabase(db_file)
        try:
            db.connect()
        except peewee.OperationalError as e:
            # If the connection is already open, ignore the exception
            if 'Connection already opened' not in str(e):
                self.console.log(f"[ERROR] {e}")

        db_list = [Profiles, Messages]
        db.create_tables([item for item in db_list], safe=True)
