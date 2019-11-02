#!/usr/bin/python
# -*- coding: utf-8 -*-

from peewee import *
import os

baza = SqliteDatabase('local.db')


def pobierz_dane_csv(plikcsv):
    kontakty = []
    assert os.path.isfile(plikcsv)
    with open(plikcsv, "r") as zawartosc:
        for linia in zawartosc:
            linia = linia.replace("\n", "")
            linia = linia.replace("\r", "")
            rekord = tuple(linia.split(","))
            kontakty.append(rekord)
    return tuple(kontakty)


class BazaModel(Model):
    class Meta:
        database = baza


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


"""Pierwsze uruchomienie"""
if not baza.table_exists(Polaczenie) or not baza.table_exists(Klient):
    baza.create_tables([Polaczenie, Klient], )
