# -*- coding: utf-8 -*-

from dialogs import *
from database import *

import wx.lib.agw.genericmessagedialog as gmd
import wx
import wx.richtext as rt

app_name = 'Dark Mail 1.0'
about_msg = 'Autor: Bartłomiej Bohdzian\n\nLicencja MIT'


# ----------------------------------------------------------------------------------------------------------------------

class Application(wx.App):

    def OnInit(self):
        wnd = MainWindow(None, -1)
        self.SetTopWindow(wnd)
        wnd.Show()

        connection_settings = Polaczenie.select().first()
        if connection_settings is None:
            Polaczenie.create(server='', port=587, user='', is_secure=False, passwd='', header='')
        return True


# ----------------------------------------------------------------------------------------------------------------------

class MainWindow(wx.Frame, object):
    wnd_width = 600
    wnd_height = 400

    def __init__(self, parent, id_):
        super(MainWindow, self).__init__(parent, id_, app_name, wx.DefaultPosition, (self.wnd_width, self.wnd_height),
                                         wx.DEFAULT_FRAME_STYLE | wx.CLIP_CHILDREN, 'Okno')
        self.SetSizeHints(400, 300)
        self.Center()
        menu_bar = MenuBar()
        self.SetMenuBar(menu_bar)
        bottom_bar = self.CreateStatusBar(2)
        bottom_bar.SetStatusWidths([93, -1])
        bottom_bar.SetStatusText('')
        bottom_bar.SetStatusText('', 1)

        MainPanel(self, -1)


# ----------------------------------------------------------------------------------------------------------------------

class MenuBar(wx.MenuBar):

    def __init__(self):
        super(MenuBar, self).__init__()

        klienci = wx.Menu()
        szablony = wx.Menu()
        wysylka = wx.Menu()
        ustawienia = wx.Menu()
        pomoc = wx.Menu()

        klienci.Append(101, '&Wczytaj z pliku..\tCtrl+O')
        klienci.Append(102, '&Wczytaj z klawiatury..\tCtrl+N')
        klienci.Append(103, '&Edytuj zaznaczony..\t')
        klienci.Append(104, '&Usuń zaznaczony..\t')

        szablony.Append(201, '&Przeglądaj\tCtrl+P')
        wysylka.Append(301, '&Wyślij\tCtrl+W')
        ustawienia.Append(401, '&Konfiguracja konta\tCtrl+K')
        pomoc.Append(501, '&O programie')

        self.Append(klienci, '&Klienci')
        self.Append(szablony, '&Szablony')
        self.Append(wysylka, '&Wysyłka')
        self.Append(ustawienia, '&Ustawienia')
        self.Append(pomoc, '&Pomoc')

        self.Bind(wx.EVT_MENU, self.read_from_file_onclick, id=101)
        self.Bind(wx.EVT_MENU, self.read_from_keyboard_onclick, id=102)
        self.Bind(wx.EVT_MENU, self.edit_onclick, id=103)
        self.Bind(wx.EVT_MENU, self.delete_onclick, id=104)
        self.Bind(wx.EVT_MENU, self.send_onclick, id=301)
        self.Bind(wx.EVT_MENU, self.config_onclick, id=401)
        self.Bind(wx.EVT_MENU, self.help_onclick, id=501)

    def read_from_file_onclick(self, event):
        panel = wx.FindWindowByName('panel')
        dlg = wx.FileDialog(self, "Wybierz plik", os.getcwd(), "", "*.csv;*.txt")
        if dlg.ShowModal() != wx.ID_OK:
            return
        path = dlg.GetPath()
        clients = pobierz_dane_csv(path)
        klienci_baza = [klient.email for klient in Klient.select()]
        new_cnt = 0
        for client in clients:
            if client[0] not in klienci_baza:
                if len(client) == 1:
                    new = Klient(email=client[0], imie='-')
                else:
                    new = Klient(email=client[0], imie=client[1])
                new.save()
                new_cnt += 1
        panel.refresh_lctrl()
        msg = '{} nowych klientów'.format(new_cnt)
        msdlg = wx.MessageDialog(self, msg, caption='Powodzenie', style=wx.OK | wx.CENTRE, pos=wx.DefaultPosition)
        msdlg.ShowModal()

    def read_from_keyboard_onclick(self, event):
        panel = wx.FindWindowByName('panel')
        dlg = WczytajDialog(wx.GetApp().GetTopWindow(), 0, 'Dodaj klienta')
        if dlg.ShowModal() == wx.ID_OK:
            var = dlg.get()
            if var:
                klienci_baza = [klient.email for klient in Klient.select()]
                if var[0] not in klienci_baza:
                    new = Klient(email=var[0], imie=var[1])
                    new.save()
                    panel.refresh_lctrl()

    def edit_onclick(self, event):
        panel = wx.FindWindowByName('panel')
        if panel.client_lctrl.GetSelectedItemCount() == 0:
            return
        i = panel.client_lctrl.GetFirstSelected()
        email = panel.client_lctrl.GetItem(i, 0).GetText()
        imie = panel.client_lctrl.GetItem(i, 1).GetText()
        edit_dlg = WczytajDialog(wx.GetApp().GetTopWindow(), 0, 'Edytuj klienta')
        edit_dlg.email_ctrl.write(email)
        edit_dlg.imie_ctrl.write(imie)
        if edit_dlg.ShowModal() != wx.ID_OK:
            return
        var = edit_dlg.get()
        inst = Klient.select().where(Klient.email == email).get()
        inst.email = var[0]
        inst.imie = var[1]
        inst.save()
        panel.refresh_lctrl()

    def delete_onclick(self, event):
        panel = wx.FindWindowByName('panel')
        if panel.client_lctrl.GetSelectedItemCount() == 0:
            return
        i = panel.client_lctrl.GetFirstSelected()
        email = panel.client_lctrl.GetItem(i).GetText()
        msg = 'Czy na pewno chcesz usunąć wybranego klienta?'
        msdlg = wx.MessageDialog(self, msg, caption='Potwierdź', style=wx.OK | wx.CANCEL, pos=wx.DefaultPosition)
        if msdlg.ShowModal() == wx.ID_OK:
            Klient.select().where(Klient.email == email).get().delete_instance()
            panel.refresh_lctrl()

    def send_onclick(self, event):
        wnd = wx.GetApp().GetTopWindow()
        try:
            wyslij_dlg = WyslijDialog(wnd, 0)
        except Exception as e:
            err = wx.MessageDialog(self, str(e), caption='Błąd', style=wx.OK, pos=wx.DefaultPosition)
            err.ShowModal()
        else:
            wyslij_dlg.ShowModal()

    def config_onclick(self, event):
        wnd = wx.GetApp().GetTopWindow()
        config_dlg = KonfigurujDialog(wnd, 0)
        config_dlg.ShowModal()

    def help_onclick(self, event):
        dlg = gmd.GenericMessageDialog(self, about_msg, app_name, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


# ----------------------------------------------------------------------------------------------------------------------

class MainPanel(wx.Panel):

    def __init__(self, parent, id_):
        super(MainPanel, self).__init__(parent, id_, name='panel')
        self.i = 0
        self.SetBackgroundColour(wx.Colour(61, 61, 61))
        self.set_gui()
        self.subject_rtext = wx.FindWindowByName('subject_rtext')
        self.content_rtext = wx.FindWindowByName('content_rtext')
        self.client_lctrl = wx.FindWindowByName('client_lctrl')
        self.client_lbl = wx.FindWindowByName('client_lbl')
        self.refresh_lctrl()

    def set_gui(self):
        top_bar = wx.Panel(self, -1)
        top_bar.SetBackgroundColour(wx.Colour(61, 161, 51))
        center_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        client_lbl = wx.StaticText(top_bar, wx.NewId(), label="0 klientow w bazie", name='client_lbl')
        client_lbl.SetForegroundColour('#ffffff')

        main_box = wx.BoxSizer(wx.VERTICAL)
        main_box.Add(top_bar, 0, wx.EXPAND, 0)
        main_box.Add(center_sizer, 1, wx.EXPAND, 0)
        main_box.Add(btn_sizer, 0, wx.EXPAND, 0)

        client_lctrl = wx.ListCtrl(self, wx.NewId(), style=wx.LC_REPORT, name='client_lctrl')
        client_lctrl.InsertColumn(0, 'e-mail')
        client_lctrl.InsertColumn(1, 'Imie')
        client_lctrl.SetColumnWidth(0, 100)
        client_lctrl.SetColumnWidth(1, 100)
        client_lctrl.SetToolTip('Klienci')
        left = wx.BoxSizer(wx.VERTICAL)
        left.Add(client_lctrl, 1, wx.EXPAND | wx.GROW | wx.RIGHT, 1)

        tresc_style = wx.VSCROLL | wx.HSCROLL | wx.NO_BORDER
        subject_rtext = wx.TextCtrl(self, wx.NewId(), size=(-1, 25), name='temat', value='Temat')
        content_rtext = rt.RichTextCtrl(self, wx.NewId(), style=tresc_style, name='tresc', value='Treść')
        right = wx.BoxSizer(wx.VERTICAL)
        right.Add(subject_rtext, 0, wx.EXPAND, 2)
        right.Add(content_rtext, 1, wx.EXPAND, 2)

        center_sizer.Add(left, 0, wx.EXPAND, 1)
        center_sizer.Add(right, 1, wx.EXPAND, 1)

        read_btn = wx.Button(self, -1, 'Wczytaj')
        spacer = wx.Panel(self, -1)
        attachment_btn = wx.Button(self, -1, 'Dodaj załącznik')
        preview_btn = wx.Button(self, -1, 'Podgląd')
        send_btn = wx.Button(self, -1, 'Wyślij')

        menu = wx.GetApp().GetTopWindow().GetMenuBar()
        read_btn.Bind(wx.EVT_BUTTON, menu.read_from_file_onclick)
        send_btn.Bind(wx.EVT_BUTTON, menu.send_onclick)

        btn_sizer.AddMany([(read_btn, 0, wx.EXPAND | wx.ALL, 1),
                           (spacer, 1, wx.EXPAND | wx.ALL, 1),
                           (attachment_btn, 0, wx.EXPAND | wx.ALL, 1),
                           (preview_btn, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 1),
                           (send_btn, 0, wx.EXPAND | wx.ALL, 1)])

        self.SetSizer(main_box)

    def refresh_lctrl(self):
        self.client_lctrl.DeleteAllItems()
        clients = Klient.select()
        client_cnt = clients.count()
        self.client_lbl.SetLabel('{} klientów w bazie'.format(client_cnt))
        for client in clients:
            self.add_line_lctrl(client.email, client.imie)
        self.i = 0

    def add_line_lctrl(self, email, name):
        self.client_lctrl.InsertItem(self.i, email)
        self.client_lctrl.SetItem(self.i, 0, email)
        self.client_lctrl.SetItem(self.i, 1, name)
        self.i += 1


# ----------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    app = Application(False)
    app.MainLoop()
