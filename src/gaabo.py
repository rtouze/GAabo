#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Main module for the gaabo app'''
import wx
import gaabo_conf
import gaabo_constants
from gaabo_controler import Controler
from subscriber import Subscriber
import sys
import panels
import datetime

class GaaboFrame(wx.Frame):

    FIELD_HEIGHT = 25
    SPECIAL_ISSUE_BTN_ID = 1

    def __init__(self, parent, title):
        #TODO Too many fields in this class
        wx.Frame.__init__(self, parent, title=title, size=(1024, 800))
        self.encoding = sys.getfilesystemencoding()
        self.controler = Controler()
        # List of the fields used to edit a subscriber
        self.field_widget_dict = {} 
        self.searched_list = []
        self.searched_name_in = None
        self.searched_company_in = None
        self.searched_email_in = None
        self.subs_dict = {}

        self.setup_status_bar()

        self.current_edited_subscriber = None
        self.parent_panel = wx.Panel(self, -1)
        self.right_panel = wx.Panel(self.parent_panel, -1)
        self.left_panel = panels.MenuBar(self)
        self.global_box = wx.BoxSizer(wx.HORIZONTAL)

        self.global_box.Add(self.left_panel, 0, wx.TOP | wx.LEFT, 10)
        self.global_box.Add(self.right_panel, 0, wx.TOP | wx.LEFT, 10)

        self.parent_panel.SetSizer(self.global_box)

        self.Centre()
        self.Show(True)

    def setup_status_bar(self):
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetFieldsCount(3)
        self.status_bar.SetStatusWidths([150, -1])
        self.status_bar.SetStatusText('Base : %s' % gaabo_conf.db_name, 0)
        self.update_subscriber_counter()

    def update_subscriber_counter(self):
        """Update number of subscriber in notification area"""
        self.status_bar.SetStatusText(
                u'Nb abonnés : %d' % self.controler.get_subscription_count(),
                2)

    def show_subscriber_creation_form(self, event):
        self.current_edited_subscriber = None
        self.get_subscriber_edition_panel()

    def refresh_window(self):
        self.global_box = wx.BoxSizer(wx.HORIZONTAL)
        self.global_box.Add(self.left_panel, 0, wx.TOP | wx.LEFT, 10)
        self.global_box.Add(self.right_panel, 0, wx.TOP | wx.LEFT, 10)
        self.parent_panel.SetSizer(self.global_box)
        self.parent_panel.Layout()

    def get_subscriber_edition_panel(self):
        self.right_panel.Destroy()
        self.right_panel = panels.EditionPanel(self)
        self.refresh_window()

    def save_subscriber_action(self, event):
        # TODO Mettre une alerte : on ne peut pas creer un abonne avec le nom ou
        # l'adresse vide !
        self.save_subscriber()
        dialog = wx.MessageDialog(
                None,
                u'L\'abonné a été sauvegardé',
                'Confirmation',
                style=wx.OK
                )
        dialog.ShowModal()
        self.status_bar.SetStatusText(u'Abonné modifié', 1)
        self.update_subscriber_counter()

    def save_subscriber(self, input_subscriber=None):
        if self.current_edited_subscriber is None:
            self.current_edited_subscriber = Subscriber()
        field_constant_list = gaabo_constants.field_names
        for key in self.field_widget_dict.keys():
            subscriber_field_name = field_constant_list[key][0]
            if subscriber_field_name == 'subscription_date':
                self.__write_date(key)
            elif self.is_integer_field(subscriber_field_name):
                self.__write_int(key)
            else:
                self.__write_field(key)

        self.current_edited_subscriber.save()

    def is_integer_field(self, field_name):
        """Check if the field must contain an integer"""
        return (
                field_name == 'hors_serie1' 
                or field_name == 'issues_to_receive'
                )

    def __write_date(self, key):
        field_value = self.field_widget_dict[key].GetValue()
        if field_value.strip() != '':
            date_array = field_value.split('/')
            self.current_edited_subscriber.subscription_date = datetime.date(
                            int(date_array[2]),
                            int(date_array[1]),
                            int(date_array[0])
                            )
        else:
            self.current_edited_subscriber.subscription_date = None

    def __write_int(self, key):
        field_value = self.field_widget_dict[key].GetValue()
        field_name = gaabo_constants.field_names[key][0]
        if field_value.isdigit():
            int_value = int(field_value)
        else:
            int_value = 0
        self.current_edited_subscriber.__dict__[field_name] = int_value

    def __write_field(self, key):
        subscriber_field_name = gaabo_constants.field_names[key][0]
        if self.encoding == 'UTF-8':
            self.current_edited_subscriber.__dict__[subscriber_field_name] = (
                    unicode(self.field_widget_dict[key].GetValue())
                    )
        else:
            self.current_edited_subscriber.__dict__[subscriber_field_name] = (
                    unicode(self.field_widget_dict[key].GetValue(), self.encoding)
                    )

    def show_search_form(self, event):
        self.right_panel.Destroy()
        self.right_panel = panels.SearchPanel(self)
        self.refresh_window()

    def search_subscriber(self, event):
        self.searched_list = []
        #TODO c'est moche, voir s'il n'y a pas une meilleur facon
        if self.encoding == 'UTF-8':
            self.searched_list.append(self.searched_name_in.GetValue())
            self.searched_list.append(self.searched_company_in.GetValue())
            self.searched_list.append(self.searched_email_in.GetValue())
        else:
            self.searched_list.append(
                    unicode(self.searched_name_in.GetValue(), self.encoding)
                    )
            self.searched_list.append(
                    unicode(self.searched_company_in.GetValue(), self.encoding)
                    )
            self.searched_list.append(
                    unicode(self.searched_email_in.GetValue(), self.encoding)
                    )

        subscriber_list = self.controler.get_searched_customer_list(
            self.searched_list[0],
            self.searched_list[1],
            self.searched_list[2]
                )
        self.get_search_panel_with_result(subscriber_list)

    def get_search_panel_with_result(self, subscriber_list):
        self.right_panel.Destroy()
        self.right_panel = panels.SearchPanel(self)
        self.right_panel.add_result(subscriber_list)
        self.refresh_window()

    def modify_subscriber_form(self, event):
        self.current_edited_subscriber = self.subs_dict[event.GetId()]
        self.get_subscriber_edition_panel()

    def delete_subscriber(self, event):
        subscriber = self.subs_dict[event.GetId()]
        dialog = wx.MessageDialog(
                None,
                u'Ètes-vous sur de vouloir supprimer l\'abonné %s ?' 
                % subscriber.lastname,
                u'Suppression d\'abonné',
                style=wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION
                )
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            self.controler.delete_subscriber(subscriber)
            self.status_bar.SetStatusText(u'Abonne supprimé', 1)
            self.search_subscriber(event)
            self.update_subscriber_counter()

    def show_empty_exporter_panel(self, event):
        if event.GetId() == self.SPECIAL_ISSUE_BTN_ID:
            self.is_special_issue = True
        else:
            self.is_special_issue = False
        self.show_exporter_panel()

    def show_exporter_panel(self, file_path=None):
        self.right_panel.Destroy()
        self.right_panel = panels.ExporterPanel(self, file_path)
        self.refresh_window()

    def export_subscriber_for_routage(self, event):
        file_path = self.right_panel.exported_file_field.GetValue()
        if self.is_special_issue is True:
            self.controler.export_special_issue_routage_file(file_path)
        else:
            self.controler.export_regular_issue_routage_file(file_path)
        dialog = wx.MessageDialog(
                None,
                u'Le fichier de routage a été créé. ' +
                u'Apres vérification, cliquer sur OK ' +
                u'pour confirmer l\'expédition du numero.',
                u'Expédition d\'un numéro',
                style=wx.OK | wx.CANCEL
                )
        if dialog.ShowModal() == wx.ID_OK:
            if self.is_special_issue is True:
                self.controler.decrement_special_issues_to_receive()
            else:
                self.controler.decrement_normal_issues_to_receive()

    def show_file_browser(self, event):
        browser = wx.FileDialog(self, "Choisir fichier de destination", style=wx.SAVE)
        if browser.ShowModal() == wx.ID_OK:
            exported_file_path = browser.GetPath()
            self.show_exporter_panel(exported_file_path)

if __name__ == '__main__':
    """NOTE: configuration
    Sous windows, le home dir est identifie comme %HOMEDRIVE%\%HOMEPATH%
    Sous *nix, c'est $HOME :)"""
    prog = wx.App(0)
    frame = GaaboFrame(None, 'GAabo')
    prog.MainLoop()
