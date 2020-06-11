from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import utils
import db
import threading
import ssl
import wx


class ReadDialog(wx.Dialog):

    def __init__(self, parent, id_, label):
        super(ReadDialog, self).__init__(parent, id_, label, wx.DefaultPosition)
        self.Center()
        self.create_gui()

        self.email_input = wx.FindWindowByName('email_input')
        self.imie_input = wx.FindWindowByName('imie_input')

    def create_gui(self):
        pnl = wx.Panel(self)

        sizer_main = wx.BoxSizer(wx.VERTICAL)
        sizer_email = wx.BoxSizer(wx.HORIZONTAL)
        sizer_imie = wx.BoxSizer(wx.HORIZONTAL)
        sizer_btn = wx.BoxSizer(wx.HORIZONTAL)

        email_lbl = wx.StaticText(pnl, 0, label="e-mail", size=(90, -1))
        email_input = wx.TextCtrl(pnl, 0, name='email_input', size=(200, -1))
        imie_lbl = wx.StaticText(pnl, 0, label="imie", size=(90, -1))
        imie_input = wx.TextCtrl(pnl, 0, name='imie_input', size=(200, -1))

        ok_btn = wx.Button(pnl, wx.ID_OK)
        anuluj_btn = wx.Button(pnl, wx.ID_CANCEL)

        sizer_email.Add(email_lbl, 0, wx.ALL, 5)
        sizer_email.Add(email_input, 0, wx.ALL, 5)

        sizer_imie.Add(imie_lbl, 0, wx.LEFT | wx.RIGHT, 5)
        sizer_imie.Add(imie_input, 0, wx.LEFT | wx.RIGHT, 5)

        sizer_btn.Add(ok_btn, 1, wx.ALL | wx.EXPAND, 5)
        sizer_btn.Add(anuluj_btn, 1, wx.ALL | wx.EXPAND, 5)

        sizer_main.Add(sizer_email, 0, wx.ALL, 5)
        sizer_main.Add(sizer_imie, 0, wx.LEFT | wx.RIGHT, 5)
        sizer_main.Add(sizer_btn, 0, wx.ALL | wx.EXPAND, 5)

        pnl.SetSizer(sizer_main)
        sizer_main.Fit(self)

    def get_inputs(self):
        return self.email_input.GetValue(), self.imie_input.GetValue()


# ----------------------------------------------------------------------------------------------------------------------

class ConfigDialog(wx.Dialog):

    def __init__(self, parent, id_):

        super(ConfigDialog, self).__init__(parent, id_, 'Konfiguracja konta', wx.DefaultPosition)
        self.Center()
        self.create_gui()

        self.server_input = wx.FindWindowByName('server_input')
        self.port_input = wx.FindWindowByName('port_input')
        self.ssl_cbox = wx.FindWindowByName('ssl_cbox')
        self.user_input = wx.FindWindowByName('user_input')
        self.passwd_input = wx.FindWindowByName('passwd_input')
        self.header_input = wx.FindWindowByName('header_input')

        self.settings = db.Polaczenie.select().first()
        self.set_gui_values()

    def create_gui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_btn = wx.BoxSizer(wx.HORIZONTAL)

        pnl = wx.Panel(self)

        server_input = wx.TextCtrl(pnl, -1, size=(180, -1), name='server_input')
        port_input = wx.TextCtrl(pnl, -1, size=(180, -1), name='port_input')
        ssl_cbox = wx.CheckBox(pnl, -1, label="Połączenie SSL", name='ssl_cbox')
        user_input = wx.TextCtrl(pnl, -1, size=(180, -1), name='user_input')
        passwd_input = wx.TextCtrl(pnl, -1, size=(180, -1), style=wx.TE_PASSWORD, name='passwd_input')
        header_input = wx.TextCtrl(pnl, -1, size=(180, -1), name='header_input')

        server_lbl = wx.StaticText(pnl, -1, 'Server', size=(90, -1))
        port_lbl = wx.StaticText(pnl, -1, 'Port', size=(90, -1))
        user_lbl = wx.StaticText(pnl, -1, 'Użytkownik', size=(90, -1))
        passwd_lbl = wx.StaticText(pnl, -1, 'Hasło', size=(90, -1))
        header_lbl = wx.StaticText(pnl, -1, 'Nagłówek nadawcy', size=(90, -1))

        ok_btn = wx.Button(pnl, -1, 'OK')
        anuluj_btn = wx.Button(pnl, -1, 'Anuluj')
        testuj_btn = wx.Button(pnl, -1, 'Testuj')

        ok_btn.Bind(wx.EVT_BUTTON, self.ok_btn_onclick)
        anuluj_btn.Bind(wx.EVT_BUTTON, self.anuluj_btn_onclick)
        port_input.Bind(wx.EVT_CHAR, utils.input_only_nums)
        testuj_btn.Bind(wx.EVT_BUTTON, self.testuj_btn_onclick)

        sizer_1.AddMany([(server_lbl, 0, wx.ALIGN_CENTER), (server_input, 0)])
        sizer_2.AddMany([(port_lbl, 0, wx.ALIGN_CENTER), (port_input, 0)])
        sizer_3.Add(ssl_cbox, 0)
        sizer_4.AddMany([(user_lbl, 0, wx.ALIGN_CENTER), (user_input, 0)])
        sizer_5.AddMany([(passwd_lbl, 0, wx.ALIGN_CENTER), (passwd_input, 0)])
        sizer_6.AddMany([(header_lbl, 0, wx.ALIGN_CENTER), (header_input, 0)])
        exc_left = wx.RIGHT | wx.TOP | wx.BOTTOM
        sizer_btn.AddMany([(ok_btn, 1, wx.ALL | wx.EXPAND, 5),
                           (anuluj_btn, 1, exc_left | wx.EXPAND, 5),
                           (testuj_btn, 1, exc_left | wx.EXPAND, 5)])
        only_bottom = wx.LEFT | wx.BOTTOM | wx.RIGHT
        main_sizer.AddMany([(sizer_1, 0, wx.EXPAND | wx.ALL, 5),
                            (sizer_2, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_3, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_4, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_5, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_6, 0, wx.EXPAND | only_bottom, 5),
                            (sizer_btn, 0, wx.EXPAND, 0)])
        pnl.SetSizer(main_sizer)
        main_sizer.Fit(self)

    def set_gui_values(self):
        self.server_input.SetValue(self.settings.server)
        self.port_input.SetValue(str(self.settings.port))
        self.ssl_cbox.SetValue(self.settings.is_secure)
        self.user_input.SetValue(self.settings.user)
        self.passwd_input.SetValue(self.settings.passwd)
        self.header_input.SetValue(self.settings.header)

    def ok_btn_onclick(self, event):
        self.settings.server = self.server_input.GetValue()
        self.settings.port = int(self.port_input.GetValue())
        self.settings.is_secure = self.ssl_cbox.GetValue()
        self.settings.user = self.user_input.GetValue()
        self.settings.passwd = self.passwd_input.GetValue()
        self.settings.header = self.header_input.GetValue()
        self.settings.save()
        self.EndModal(0)

    def anuluj_btn_onclick(self, event):
        self.EndModal(0)

    def testuj_btn_onclick(self, event):
        serv = self.server_input.GetValue()
        port = self.port_input.GetValue()
        usr = self.user_input.GetValue()
        passwd = self.passwd_input.GetValue()
        secure = self.ssl_cbox.GetValue()
        button = event.GetEventObject()

        try:
            with SMTP(serv, port, timeout=5) as server:
                if secure is True:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                server.login(usr, passwd)
                button.SetBackgroundColour('#6ab04c')
        except Exception as e:
            msg = wx.MessageDialog(self, str(e), caption='Błąd', style=wx.OK, pos=wx.DefaultPosition)
            msg.ShowModal()
            button.SetBackgroundColour('#eb4d4b')


# ----------------------------------------------------------------------------------------------------------------------

class SendDialog(wx.Dialog):

    def __init__(self, parent, id_):
        super(SendDialog, self).__init__(parent, id_, 'Wysyłanie', wx.DefaultPosition, (400, 200))
        self.Center()
        self.settings = db.Polaczenie.select().first()
        try:
            self.server = self.create_server()
        except Exception as e:
            raise Exception('Błąd połączenia SMTP. Sprawdź konfigurację')
        self.create_gui()
        self.prgs_gg = wx.FindWindowByName('progress_gg')
        self.adres_lbl = wx.FindWindowByName('adres_lbl')
        self.wyslij_btn = wx.FindWindowByName('wyslij_btn')

    def create_server(self):
        try:
            server = SMTP(self.settings.server, self.settings.port, timeout=5)
            if self.settings.is_secure is True:
                context = ssl.create_default_context()
                server.ehlo()
                server.starttls(context=context)
            server.login(self.settings.user, self.settings.passwd)
        except Exception as e:
            raise Exception(e)
        return server

    def create_gui(self):
        pnl = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        adres_stc = wx.StaticText(pnl, label='Adres', name='adres_stc')
        adres_lbl = wx.StaticText(pnl, label='-', name='adres_lbl')
        counter_lbl = wx.StaticText(pnl, label='0/0', name='counter_lbl')

        top_sizer.AddMany([(adres_stc, 0, wx.ALL, 5),
                           (adres_lbl, 0, wx.ALL, 5),
                           (counter_lbl, 0, wx.ALL, 5)])

        progres_gg = wx.Gauge(pnl, 0, 100, size=(250, 25), style=wx.GA_HORIZONTAL, name='progress_gg')

        wyslij_btn = wx.Button(pnl, -1, label="Wyslij", name='wyslij_btn')
        wyslij_btn.Bind(wx.EVT_BUTTON, self.wyslij_btn_onclick)

        anuluj_btn = wx.Button(pnl, -1, label="Anuluj", name='anuluj_btn')
        anuluj_btn.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())

        btn_sizer.AddMany([(anuluj_btn, 0, wx.ALIGN_LEFT | wx.ALL, 5),
                           (wyslij_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 5)])

        main_sizer.AddMany([(top_sizer, 1, wx.ALL, 5),
                            (progres_gg, 1, wx.ALL | wx.EXPAND, 5),
                            (btn_sizer, 1, wx.ALL | wx.EXPAND, 5)])
        pnl.SetSizer(main_sizer)
        main_sizer.Fit(self)

    def wyslij_btn_onclick(self, event):
        thread = threading.Thread(target=self.sending_thread)
        thread.start()
        # clients_num = self.clients.count()
        # self.prgs_gg.SetRange(clients_num)

    def create_message(self, address):
        message = MIMEMultipart('alternative')
        message['Subject'] = wx.FindWindowByName('temat').GetValue()
        message['From'] = self.settings.header + '<' + self.settings.user + '>'
        message['To'] = address
        text = wx.FindWindowByName('tresc').GetValue()
        html = wx.FindWindowByName('tresc').GetValue()
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        message.attach(part1)
        message.attach(part2)
        return message.as_string()

    def sending_thread(self):
        for client in db.Klient.select():
            address = client.email
            message = self.create_message(address)
            try:
                self.server.sendmail(self.settings.user, address, message)
                print('Wyslano ' + recipient)
            except Exception as e:
                print('Nie wyslano do ' + address + ' Powód:' + str(e))
        print('Zakończono pomyslnie ')
        self.Destroy()
