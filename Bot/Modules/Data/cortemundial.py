import os
import sys

from peewee import Model, CharField, SqliteDatabase, DateTimeField, BooleanField, TextField, IntegerField, \
    ForeignKeyField, FloatField
from pathlib import Path

db = SqliteDatabase("C:\\Users\\joaoluis.santos\\PycharmProjects\\Mestre-Sara-a-taveneira\Bot\\Data\\corte.db")

# USER PROFILING

class Profiles(Model):
    username = CharField(unique=True)
    userid = CharField(unique=True)
    discriminator = CharField()
    avatar_url = CharField(null=True)
    status = CharField(default="offline")
    last_seen = DateTimeField(null=True)
    joined_at = DateTimeField(null=True)
    is_bot = BooleanField(default=False)
    last_interaction = DateTimeField(null=True)
    created_at = DateTimeField(null=True)

    class Meta:
        database = db


class Messages(Model):
    user = ForeignKeyField(Profiles, backref='messages')  # Links to Profiles
    message_id = CharField(unique=True)  # Unique Discord message ID
    message_text = TextField()
    timestamp = DateTimeField()
    message_type = CharField(default='text')
    channel_id = CharField(null=True)
    guild_id = CharField(null=True)

    class Meta:
        database = db

