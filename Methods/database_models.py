from peewee import Model, CharField, SqliteDatabase

db = SqliteDatabase("MestreSaraData/memory.db")


class Whitelist(Model):
    userid = CharField(unique=True)

    class Meta:
        database = db

class Censura(Model):
    palavra = CharField()

    class Meta:
        database = db
