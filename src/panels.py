#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This modules provides the panel classes available for the GUI"""

import wx
import gaabo_constants

FIELD_HEIGHT = 25

class MenuBar(wx.Panel):
    """This class represent the menubar, AKA the left panel of the GUI"""

    def __init__(self, frame):
        """Initialize the panel and set the bind functions using the parent
        frame methods. When its called, the frame must have a parent panel
        created."""
        wx.Panel.__init__(self, frame.parent_panel, -1)

        button_create = wx.Button(self, -1, u'Créer abonné')
        button_modify = wx.Button(self, -1, u'Modifier / Supprimer abonné')
        button_send_issue = wx.Button(self, -1, u'Expédier nouveau numéro')
        button_send_special_issue = wx.Button(
                self,
                frame.SPECIAL_ISSUE_BTN_ID,
                u'Expédier un hors-serie'
                )
        button_ending_sub = wx.Button(self, -1, u'Abonnés en fin d\'abonnement')

        menu_buttons_grid = wx.GridSizer(5, 1, 10, 0)
        menu_buttons_grid.Add(button_create)
        menu_buttons_grid.Add(button_modify)
        menu_buttons_grid.Add(button_send_issue)
        menu_buttons_grid.Add(button_send_special_issue)
        menu_buttons_grid.Add(button_ending_sub)
        self.SetSizer(menu_buttons_grid)

        frame.Bind(wx.EVT_BUTTON, frame.show_subscriber_creation_form, id=button_create.GetId())
        frame.Bind(wx.EVT_BUTTON, frame.show_search_form, id=button_modify.GetId())
        frame.Bind(wx.EVT_BUTTON, frame.show_empty_exporter_panel, id=button_send_issue.GetId())
        frame.Bind(wx.EVT_BUTTON, frame.show_empty_exporter_panel, id=frame.SPECIAL_ISSUE_BTN_ID)
        frame.Bind(wx.EVT_BUTTON, frame.show_ending_subscription, id=button_ending_sub.GetId())

#####

class EditionPanel(wx.Panel):
    """This class represent the subscriber edition panel"""

    def __init__(self, frame):
        """Initialize the panel and set the bind functions using the parent
        frame methods. When its called, the frame must have a parent panel
        created."""
        wx.Panel.__init__(self, frame.parent_panel, -1)

        box = wx.BoxSizer(wx.VERTICAL)
        self.frame = frame
        self.current_edited_subscriber = frame.current_edited_subscriber
        box.Add(self.get_panel_title())
        grid = wx.FlexGridSizer(20, 2, 5, 5)
        self.pairs = []
        self.generate_pair_list()

        for pair in self.pairs:
            grid.Add(pair[0])
            grid.Add(pair[1])

        box.Add(grid)
        box.Add(self.generate_button_box())
        self.SetSizer(box)

    def get_panel_title(self):
        """Generate the title of the panel, wether we are creating a new
        subscriber or editing a new one."""
        if self.current_edited_subscriber is None:
            return wx.StaticText(self, -1, u'Édition d\'un nouvel abonne\n')
        else:
            return wx.StaticText(self, -1, u'Édition de l\'abonne\n')

    def generate_pair_list(self):
        """Generate the list of field names, field values pairs)."""
        index = 0
        for items in gaabo_constants.field_names:
            self.pairs.append(self.get_subscriber_edition_pairs(index))
            index += 1
    
    def get_subscriber_edition_pairs(self, field_label_id):
        """Generate a pair of field name + field value"""
        field_constant_list = gaabo_constants.field_names
        displayed_field_name = field_constant_list[field_label_id][1]
        label = wx.StaticText(self, -1, displayed_field_name)
        if self.current_edited_subscriber is None:
            self.frame.field_widget_dict[field_label_id] = wx.TextCtrl(
                    self,
                    -1,
                    size=(200, FIELD_HEIGHT)
                    )
        else:
            #TODO il faudra faire varier selon les types de champ
            subscriber_field_name = field_constant_list[field_label_id][0]
            self.frame.field_widget_dict[field_label_id] = wx.TextCtrl(
                    self,
                    -1,
                    unicode(
                        self.frame.current_edited_subscriber.__dict__[subscriber_field_name]
                        ),
                    size=(200, FIELD_HEIGHT)
                    )
        return (label, self.frame.field_widget_dict[field_label_id])

    def generate_button_box(self):
        """Generate the OK buton pqrt with the action binding"""
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, -1, 'Ok')
        button_box.Add(ok_button)
        self.frame.Bind(
                wx.EVT_BUTTON,
                self.frame.save_subscriber_action,
                id=ok_button.GetId()
                )
        return button_box

#####

class SearchPanel(wx.Panel):
    """Class that represent the search panel"""

    def __init__(self, frame):
        # TODO mettre un tooltip pour aider a la recherche
        wx.Panel.__init__(self, frame.parent_panel, -1)
        self.frame = frame
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.generate_search_box()
        self.SetSizer(self.box)

    def generate_search_box(self):
        """Generate the search part of the search panel"""
        self.box.Add(wx.StaticText(self, -1, u'Entrer les critères de recherche :\n'))
        grid = wx.FlexGridSizer(2, 2, 5, 5)
        grid.Add(wx.StaticText(self, -1, 'Nom de famille'))
        if len(self.frame.searched_pair) < 1:
            self.frame.searched_name_in = wx.TextCtrl(self, -1, size=(200, 20))
        else:
            self.frame.searched_name_in = wx.TextCtrl(self, -1, self.frame.searched_pair[0], size=(200, 20))
        grid.Add(self.frame.searched_name_in)
        grid.Add(wx.StaticText(self, -1, u'Nom société'))
        if len(self.frame.searched_pair) < 2:
            self.frame.searched_company_in = wx.TextCtrl(self, -1, size=(200, 20))
        else:
            self.frame.searched_company_in = wx.TextCtrl(self, -1, self.frame.searched_pair[1], size=(200, 20))
        grid.Add(self.frame.searched_company_in)
        self.box.Add(grid)
        search_button = wx.Button(self, -1, u'Rechercher')
        self.frame.Bind(wx.EVT_BUTTON, self.frame.search_subscriber, id=search_button.GetId())
        self.box.Add(search_button)

    def add_result(self, subscriber_list):
        """Public method to add the result part made of the subscribers objects
        in the subscriber list"""
        self.add_separation_to_box()
        self.add_result_to_box(subscriber_list)
        self.SetSizer(self.box)

    def add_separation_to_box(self):
        """Add a separation line between the search fields and the result"""
        self.box.Add(wx.StaticText(self, -1, ''))
        self.box.Add(wx.StaticLine(self, wx.HORIZONTAL, size=(350, 1)))
        self.box.Add(wx.StaticText(self, -1, ''))

    def add_result_to_box(self, subscriber_list):
        """Add the result grid to the box, member of SearchPanel instance."""
        self.result_grid = wx.FlexGridSizer(len(subscriber_list) + 1, 5, 5, 5)
        self.add_heading_to_result_grid()
        self.add_subscriber_to_result_grid(subscriber_list)
        self.box.Add(self.result_grid)

    def add_heading_to_result_grid(self):
        """Add the header line to the result grid"""
        self.result_grid.Add(self.get_heading_text('Nom'))
        self.result_grid.Add(self.get_heading_text(u'Prénom'))
        self.result_grid.Add(self.get_heading_text(u'Société'))
        self.result_grid.Add(self.get_heading_text('Action'))
        self.result_grid.Add(wx.StaticText(self, -1, ''))

    def get_heading_text(self, text):
        """Returns a StaticText with a heading style"""
        heading_text = wx.StaticText(self, -1, text)
        heading_font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        heading_text.SetFont(heading_font)
        return heading_text

    def add_subscriber_to_result_grid(self, subscriber_list):
        "Add content of the list to the result grid"""
        # Dictionnaire pour stocker les paires button_id / subscriber
        self.frame.subs_dict = {}
        for subscriber in subscriber_list:
            modify_button = wx.Button(self, -1, 'Modifier')
            delete_button = wx.Button(self, -1, 'Supprimer')
            modify_button_id = modify_button.GetId()
            delete_button_id = delete_button.GetId()
            self.frame.subs_dict[modify_button_id] = subscriber
            self.frame.subs_dict[delete_button_id] = subscriber
            self.frame.Bind(
                    wx.EVT_BUTTON,
                    self.frame.modify_subscriber_form,
                    id=modify_button_id
                    )
            self.frame.Bind(
                    wx.EVT_BUTTON,
                    self.frame.delete_subscriber,
                    id=delete_button_id
                    )

            self.result_grid.Add(
                    wx.StaticText(self, -1, subscriber.lastname),
                    flag=wx.ALIGN_CENTER_VERTICAL
                    )
            self.result_grid.Add(
                    wx.StaticText(self, -1, subscriber.firstname),
                    flag=wx.ALIGN_CENTER_VERTICAL
                    )
            self.result_grid.Add(
                    wx.StaticText(self, -1, subscriber.company),
                    flag=wx.ALIGN_CENTER_VERTICAL
                    )
            self.result_grid.Add(modify_button, flag=wx.ALIGN_CENTER_VERTICAL)
            self.result_grid.Add(delete_button, flag=wx.ALIGN_CENTER_VERTICAL)
#####

class ExporterPanel(wx.Panel):
    def __init__(self, frame, file_path=None):
        wx.Panel.__init__(self, frame.parent_panel, -1)
        self.frame = frame
        if file_path is None:
            file_path = ''
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(wx.StaticText(self, -1, u'Exporter données vers fichier de routage\n'))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(self, -1, u'Fichier a générer '))
        self.exported_file_field = wx.TextCtrl(self, -1, file_path, size=(200, FIELD_HEIGHT))
        hbox.Add(self.exported_file_field)
        browse_button = wx.Button(self, -1, 'Parcourir')
        hbox.Add(browse_button)

        box.Add(hbox)
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, -1, 'Ok')
        button_box.Add(ok_button)
        box.Add(button_box)
        self.frame.Bind(
                wx.EVT_BUTTON,
                self.frame.show_file_browser,
                id=browse_button.GetId()
                )
        self.frame.Bind(
                wx.EVT_BUTTON,
                self.frame.export_subscriber_for_routage,
                id=ok_button.GetId()
                )
        self.SetSizer(box)
