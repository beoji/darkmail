from peewee import *

import os

sqlite_db = SqliteDatabase('local.db')


class BazaModel(Model):
    class Meta:
        database = sqlite_db


class Klient(BazaModel):
    email = CharField(null=False)
    imie = CharField(null=True)


class Polaczenie(BazaModel):
    server = CharField(null=False)
    port = IntegerField(null=False)
    is_secure = BooleanField(null=False)
    user = CharField(null=False)
    passwd = CharField(null=False)
    header = CharField(null=False)


if not sqlite_db.table_exists(Polaczenie) or not sqlite_db.table_exists(Klient):
    sqlite_db.create_tables([Polaczenie, Klient], )
