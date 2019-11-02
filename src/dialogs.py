#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

from database import *
from functions import *
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import threading
import ssl
import wx


class WczytajDialog(wx.Dialog):

    def __init__(self, parent, id_, label):
        super(WczytajDialog, self).__init__(parent, id_, label, wx.DefaultPosition)
        self.Center()
        self.panel = wx.Panel(self)

        sizer0 = wx.BoxSizer(wx.VERTICAL)

        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)

        email_info = wx.StaticText(self.panel, wx.NewId(), label="e-mail", size=(90, -1))
        self.email_ctrl = wx.TextCtrl(self.panel, wx.NewId())
        imie_ctrl_info = wx.StaticText(self.panel, wx.NewId(), label="imie", size=(90, -1))
        self.imie_ctrl = wx.TextCtrl(self.panel, wx.NewId())

        ok_btn = wx.Button(self.panel, wx.ID_OK)
        cancel = wx.Button(self.panel, wx.ID_CANCEL)

        sizer1.Add(email_info, 1, wx.ALL | wx.EXPAND)
        sizer1.Add(self.email_ctrl, 2, wx.ALL | wx.EXPAND)

        sizer2.Add(imie_ctrl_info, 1, wx.ALL | wx.EXPAND)
        sizer2.Add(self.imie_ctrl, 2, wx.ALL | wx.EXPAND)

        sizer3.Add(ok_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        sizer3.Add(cancel, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        sizer0.Add(sizer1, 0, wx.ALL, 5)
        sizer0.Add(sizer2, 0, wx.ALL, 5)
        sizer0.Add(sizer3, 0, wx.ALL, 5)

        self.panel.SetSizer(sizer0)
        sizer0.Fit(self)

    def get(self):
        return self.email_ctrl.GetValue(), self.imie_ctrl.GetValue()


# ----------------------------------------------------------------------------------------------------------------------

class KonfigurujDialog(wx.Dialog):

    def __init__(self, parent, id_):

        super(KonfigurujDialog, self).__init__(parent, id_, 'Konfiguracja konta', wx.DefaultPosition)
        self.Center()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_btn = wx.BoxSizer(wx.HORIZONTAL)

        settings = Polaczenie.select().first()

        self.panel = wx.Panel(self)

        self.server_input = wx.TextCtrl(self.panel, -1, settings.server, size=(180, -1))
        self.port_input = wx.TextCtrl(self.panel, -1, str(settings.port), size=(180, -1))
        self.ssl_cbox = wx.CheckBox(self.panel, -1, label="Połączenie SSL", name=wx.CheckBoxNameStr)
        if settings.is_secure is True:
            self.ssl_cbox.SetValue(True)
        self.user_input = wx.TextCtrl(self.panel, -1, settings.user, size=(180, -1))
        self.passwd_input = wx.TextCtrl(self.panel, -1, settings.passwd, size=(180, -1), style=wx.TE_PASSWORD)
        self.header_input = wx.TextCtrl(self.panel, -1, settings.header, size=(180, -1))

        server_text = wx.StaticText(self.panel, -1, 'Server', size=(90, -1))
        port_text = wx.StaticText(self.panel, -1, 'Port', size=(90, -1))
        user_text = wx.StaticText(self.panel, -1, 'Użytkownik', size=(90, -1))
        passwd_text = wx.StaticText(self.panel, -1, 'Hasło', size=(90, -1))
        header_text = wx.StaticText(self.panel, -1, 'Nagłówek nadawcy', size=(90, -1))

        ok_btn = wx.Button(self.panel, -1, 'OK')
        anuluj_btn = wx.Button(self.panel, wx.ID_CANCEL, 'Anuluj')
        self.testuj_btn = wx.Button(self.panel, -1, 'Testuj')

        ok_btn.Bind(wx.EVT_BUTTON, self.ok_btn_onclick)
        self.port_input.Bind(wx.EVT_CHAR, input_only_nums)
        self.testuj_btn.Bind(wx.EVT_BUTTON, self.testuj_btn_onclick)

        sizer_1.AddMany([(server_text, 0, wx.ALIGN_CENTER), (self.server_input, 0)])
        sizer_2.AddMany([(port_text, 0, wx.ALIGN_CENTER), (self.port_input, 0)])
        sizer_3.Add(self.ssl_cbox, 0, wx.ALIGN_RIGHT)
        sizer_4.AddMany([(user_text, 0, wx.ALIGN_CENTER), (self.user_input, 0)])
        sizer_5.AddMany([(passwd_text, 0, wx.ALIGN_CENTER), (self.passwd_input, 0)])
        sizer_6.AddMany([(header_text, 0, wx.ALIGN_CENTER), (self.header_input, 0)])
        sizer_btn.AddMany([(ok_btn, 0, wx.RIGHT, 5),
                           (anuluj_btn, 0, wx.RIGHT, 5),
                           (self.testuj_btn, 0)])
        only_bottom = wx.LEFT | wx.BOTTOM | wx.RIGHT
        main_sizer.AddMany([(sizer_1, 0, wx.EXPAND | wx.ALL, 5),
                            (sizer_2, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_3, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_4, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_5, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_6, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_btn, 0, wx.EXPAND | wx.ALIGN_CENTER | only_bottom, 5)])
        self.panel.SetSizer(main_sizer)
        main_sizer.Fit(self)

    def ok_btn_onclick(self, event):
        settings = Polaczenie.select().first()
        settings.server = self.server_input.GetValue()
        settings.port = int(self.port_input.GetValue())
        settings.is_secure = self.ssl_cbox.GetValue()
        settings.user = self.user_input.GetValue()
        settings.passwd = self.passwd_input.GetValue()
        settings.header = self.header_input.GetValue()
        settings.save()
        self.Close()

    def testuj_btn_onclick(self, event):
        serv = self.server_input.GetValue()
        port = self.port_input.GetValue()
        usr = self.user_input.GetValue()
        passwd = self.passwd_input.GetValue()

        try:
            with SMTP(serv, port, timeout=5) as server:
                if self.ssl_cbox.GetValue() is True:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                server.login(usr, passwd)
                self.testuj_btn.SetBackgroundColour('#6ab04c')
        except Exception as e:
            msg = wx.MessageDialog(self, str(e), caption='Błąd', style=wx.OK, pos=wx.DefaultPosition)
            msg.ShowModal()
            self.testuj_btn.SetBackgroundColour('#eb4d4b')


# ----------------------------------------------------------------------------------------------------------------------

class WyslijDialog(wx.Dialog):

    def __init__(self, parent, id_):
        super(WyslijDialog, self).__init__(parent, id_, 'Wysyłanie', wx.DefaultPosition, (400, 200))
        self.settings = Polaczenie.select().first()
        try:
            self.server = self.create_server()
        except Exception as e:
            raise Exception(e, 'Błąd połączenia SMTP. Sprawdź konfigurację')
        self.create_gui()
        self.prgs_gg = wx.FindWindowByName('progress_gg')
        self.adres_lbl = wx.FindWindowByName('adres_lbl')
        self.wyslij_btn = wx.FindWindowByName('wyslij_btn')
        self.clients = Klient.select()

    def create_server(self):
        try:
            server = SMTP(self.settings.server, self.settings.port, timeout=5)
            if self.settings.is_secure is True:
                context = ssl.create_default_context()
                server.starttls(context=context)
            server.login(self.settings.user, self.settings.passwd)
        except Exception as e:
            raise Exception(e)
        return server

    def create_gui(self):
        self.Center()
        panel = wx.Panel(self)
        adres_stc = wx.StaticText(panel, label='Adres', name='adres_stc')
        adres_lbl = wx.StaticText(panel, label='-', name='adres_lbl')
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.AddMany([(adres_stc, 0, wx.ALL, 5),
                         (adres_lbl, 0, wx.ALL, 5)])
        progres_gg = wx.Gauge(panel, 0, 100, size=(250, 25), style=wx.GA_HORIZONTAL, name='progress_gg')
        wyslij_btn = wx.Button(panel, -1, label="Wyslij", name='wyslij_btn')
        wyslij_btn.Bind(wx.EVT_BUTTON, self.wyslij_btn_onclick)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddMany([(sizer_1, 1, wx.ALL, 5),
                            (progres_gg, 1, wx.ALL, 5),
                            (wyslij_btn, 1, wx.ALIGN_RIGHT, 5)], )
        panel.SetSizer(main_sizer)
        main_sizer.Fit(self)

    def wyslij_btn_onclick(self, event):
        thread = threading.Thread(target=self.sending_thread)
        thread.start()
        # clients_num = self.clients.count()
        # self.prgs_gg.SetRange(clients_num)

    def create_message(self, recipient):
        message = MIMEMultipart('alternative')
        message['Subject'] = wx.FindWindowByName('temat').GetValue()
        message['From'] = self.settings.header + '<' + self.settings.user + '>'
        message['To'] = recipient
        text = wx.FindWindowByName('tresc').GetValue()
        html = wx.FindWindowByName('tresc').GetValue()
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        message.attach(part1)
        message.attach(part2)
        return message.as_string()

    def sending_thread(self):
        for client in self.clients:
            recipient = client.email
            message = self.create_message(recipient)
            try:
                self.server.sendmail(self.settings.user, recipient, message)
                print('Wyslano ' + recipient)
            except Exception as e:
                print('Nie wyslano do ' + recipient + ' Powód:' + str(e))
        print('Zakończono pomyslnie ')
