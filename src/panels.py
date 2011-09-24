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

        self.frame = frame
        self.buttons = {} 
        self.create_buttons()
        self.put_buttons_in_grid()
        self.bind_events()

    def create_buttons(self):
        """Create the buttons that will be in the MenuBar"""
        self.buttons['create'] = \
                wx.Button(self, -1, u'Créer abonné')
        self.buttons['modify'] = \
                wx.Button(self, -1, u'Modifier / Supprimer abonné')
        self.buttons['send_issue'] = \
                wx.Button(self, -1, u'Expédier nouveau numéro')
        self.buttons['send_special_issue'] = wx.Button(
                self,
                self.frame.SPECIAL_ISSUE_BTN_ID,
                u'Expédier un hors-serie'
                )
        self.buttons['gen_mailing'] = wx.Button(
                self,
                self.frame.SPECIAL_ISSUE_BTN_ID,
                u'Génération liste de mailing'
                )
        self.buttons['gen_paper_mailing'] = wx.Button(
                self,
                self.frame.SPECIAL_ISSUE_BTN_ID,
                u'Génération liste mailing papier'
                )

    def put_buttons_in_grid(self):
        """Generate a GridSizer that will contain the buttons"""
        menu_buttons_grid = wx.GridSizer(6, 1, 10, 0)
        menu_buttons_grid.Add(self.buttons['create'])
        menu_buttons_grid.Add(self.buttons['modify'])
        menu_buttons_grid.Add(self.buttons['send_issue'])
        menu_buttons_grid.Add(self.buttons['send_special_issue'])
        menu_buttons_grid.Add(self.buttons['gen_mailing'])
        menu_buttons_grid.Add(self.buttons['gen_paper_mailing'])
        self.SetSizer(menu_buttons_grid)

    def bind_events(self):
        """Bind events to button in the menubar"""
        self.bind_btn_evt(
                self.frame.show_subscriber_creation_form,
                self.buttons['create']
                ) 
        self.bind_btn_evt(
                self.frame.show_search_form,
                self.buttons['modify']
                ) 
        self.bind_btn_evt(
                self.frame.show_empty_exporter_panel,
                self.buttons['send_issue']
                ) 
        self.bind_btn_evt(
                self.frame.show_empty_exporter_panel,
                self.buttons['send_special_issue']
                ) 
        self.bind_btn_evt(
                self.frame.generate_mailing_list,
                self.buttons['gen_mailing']
                ) 
        self.bind_btn_evt(
                self.frame.generate_paper_mailing_list,
                self.buttons['gen_paper_mailing']
                ) 

    def bind_btn_evt(self, method, button):
        """Bind a callback to a button press event"""
        self.frame.Bind(
                wx.EVT_BUTTON,
                method,
                id=button.GetId()
                )

class EditionPanel(wx.Panel):
    """This class represent the subscriber edition panel"""

    def __init__(self, frame):
        """Initialize the panel and set the bind functions using the parent
        frame methods. When its called, the frame must have a parent panel
        created."""
        wx.Panel.__init__(self, frame.parent_panel, -1)

        box = wx.BoxSizer(wx.VERTICAL)
        self.frame = frame
        box.Add(self.get_panel_title())
        grid = wx.FlexGridSizer(20, 2, 5, 5)
        self.pairs = []
        self.controler = self.frame.controler
        #self.generate_pair_list()

        for field_pair in gaabo_constants.field_names:
            key = field_pair[0]
            field = field_pair[1]
            grid.Add(wx.StaticText(self, -1, field), flag=wx.ALIGN_CENTER_VERTICAL)
            if key in self.controler.subscriber_values.keys():
                value = unicode(self.controler.subscriber_values[key])
            else:
                value = None
            self.controler.field_widget_dict[key] = self.set_text_field(value)
            grid.Add(self.controler.field_widget_dict[key], flag=wx.ALIGN_CENTER_VERTICAL) 
        box.Add(grid)
        box.Add(self.generate_button_box())
        self.SetSizer(box)

    def get_panel_title(self):
        """Generate the title of the panel, wether we are creating a new
        subscriber or editing a new one."""
        if len(self.frame.subscriber_values) == 0:
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
        internal_field_name = field_constant_list[field_label_id][0]
        subscriber_field_name = field_constant_list[field_label_id][0]
        if subscriber_field_name == 'subscription_date':
            label = wx.StaticText(
                    self,
                    -1,
                    displayed_field_name + ' (jj/mm/aaaa)'
                    )
        else:
            label = wx.StaticText(self, -1, displayed_field_name)

        if self.subscriber is None:
            self.frame.field_widget_dict[field_label_id] = wx.TextCtrl(
                    self,
                    -1,
                    size=(200, FIELD_HEIGHT)
                    )
        else:
            if subscriber_field_name == 'subscription_date':
                subscr_date = self.subscriber.subscription_date
                field_value = None
                if subscr_date is not None:
                    field_value = subscr_date.strftime('%d/%m/%Y')

                self.frame.field_widget_dict[field_label_id] = \
                        self.set_text_field(field_value)

            elif subscriber_field_name == 'post_code':
                post_code = self.subscriber.address.post_code
                formatted_post_code = ''
                if (unicode(post_code).isdigit() and post_code != 0):
                    formatted_post_code = '%05d' % post_code
                self.frame.field_widget_dict[field_label_id] = \
                        self.set_text_field(formatted_post_code)
            elif subscriber_field_name == 'address':
                field_value = self.subscriber.address.address1
                self.frame.field_widget_dict[field_label_id] = \
                        self.set_text_field(field_value)
            elif subscriber_field_name == 'address_addition':
                field_value = self.subscriber.address.address2
                self.frame.field_widget_dict[field_label_id] = \
                        self.set_text_field(field_value)
            elif subscriber_field_name == 'city':
                field_value = self.subscriber.address.city
                self.frame.field_widget_dict[field_label_id] = \
                        self.set_text_field(field_value)

            else:
                field_value = self.subscriber.__dict__[subscriber_field_name]
                self.frame.field_widget_dict[field_label_id] = \
                        self.set_text_field(field_value)
        return (label, self.frame.field_widget_dict[field_label_id])

    def set_text_field(self, field_value=None):
        """Returns an unicode formated TextCtrl containing field_value"""
        if field_value is None:
            widget = wx.TextCtrl(
                    self,
                    -1,
                    size=(200, FIELD_HEIGHT)
                    )
        else:
            widget = wx.TextCtrl(
                    self,
                    -1,
                    unicode(field_value),
                    size=(200, FIELD_HEIGHT)
                    )
        return widget

    def generate_button_box(self):
        """Generate the OK buton pqrt with the action binding"""
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        ok_button = wx.Button(self, -1, 'Ok')
        button_box.Add(ok_button)

        self.frame.Bind(
                wx.EVT_BUTTON,
                self.controler.save_subscriber_action,
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
        grid = wx.FlexGridSizer(3, 2, 5, 5)

        self.__add_name_search_field(grid)

        self.__add_company_search_field(grid)

        self.__add_email_search_field(grid)

        self.box.Add(grid)
        search_button = wx.Button(self, -1, u'Rechercher')
        self.frame.Bind(wx.EVT_BUTTON, self.frame.search_subscriber, id=search_button.GetId())
        self.box.Add(search_button)

    def __add_name_search_field(self, grid):
        grid.Add(wx.StaticText(self, -1, 'Nom de famille'), flag=wx.ALIGN_CENTER_VERTICAL)
        self.frame.searched_name_in = self.__get_common_search_field(1)
        grid.Add(self.frame.searched_name_in, flag=wx.ALIGN_CENTER_VERTICAL)

    def __add_company_search_field(self, grid):
        grid.Add(wx.StaticText(self, -1, u'Nom société'), flag=wx.ALIGN_CENTER_VERTICAL)
        self.frame.searched_company_in = self.__get_common_search_field(2)
        grid.Add(self.frame.searched_company_in, flag=wx.ALIGN_CENTER_VERTICAL)

    def __add_email_search_field(self, grid):
        grid.Add(wx.StaticText(self, -1, u'Adresse email'), flag=wx.ALIGN_CENTER_VERTICAL)
        self.frame.searched_email_in = self.__get_common_search_field(3)
        grid.Add(self.frame.searched_email_in, flag=wx.ALIGN_CENTER_VERTICAL)

    def __get_common_search_field(self, field_position):
        """We assume that field_position is > 0. No control implemented."""
        sizing_pair = (200, FIELD_HEIGHT)
        field_index = field_position - 1

        if len(self.frame.searched_list) < field_position:
            field = wx.TextCtrl( self, -1, size=sizing_pair)
        else:
            field = wx.TextCtrl(
                    self,
                    -1,
                    self.frame.searched_list[field_index],
                    size=sizing_pair
                    )
        return field

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
