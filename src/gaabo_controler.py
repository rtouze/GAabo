#!/usr/bin/env python
"""This module contains a controler to make gaabo works"""

__author__ = 'romain.touze@gmail.com'

from datetime import date
from subscriber import Subscriber
from subscriber import Address
from subscriber_exporter import RoutageExporter

class Controler(object):
    def __init__(self, frame):
        """Initialization of the controler. Uses the frame as parameter to send
        it info"""
        self.subscriber_values = {}
        self.field_widget_dict = {}
        self.frame = frame

    def get_searched_customer_list(self, lastname, company, email):
        """Retrieves a subscriber dictionary using its lastname, company or
        email"""
        # TODO improve : retrieve id, lastname, company then retrieve the
        # customer when edition is demanded
        # TODO : rename fonction to get_searched_subscriber_list
        # TODO: split it!
        subs_list = [] 
        if lastname:
            subs_list.extend(
                    SubscriberAdapter.get_subscribers_from_lastname(lastname)
                    )
        if company:
            subs_list.extend(
                    SubscriberAdapter.get_subscribers_from_company(company)
                    )
        if email:
            subs_list.extend(
                    SubscriberAdapter.get_subscribers_from_email(email)
                    )

        identifiers = []
        index = 0
        for subscriber in subs_list:
            if subscriber['subscriber_id'] in identifiers:
                subs_list.pop(index)
            else:
                identifiers.append(subscriber['subscriber_id'])
            index += 1
        
        return subs_list

    def delete_subscriber(self):
        """Delete current subscriber"""
        SubscriberAdapter.delete_from_id(
                self.subscriber_values['subscriber_id']
                )

    def export_regular_issue_routage_file(self, file_path):
        """Create the file to send to routing service"""
        # TODO rename the method (use routing)
        # TODO set it as function for pylint :)
        exporter = RoutageExporter(file_path)
        exporter.do_export()

    def decrement_normal_issues_to_receive(self):
        """Decrement issues to receive when exported file is validated"""
        Subscriber.decrement_issues_to_receive()

    def decrement_special_issues_to_receive(self):
        """Decrement special issues to receive when exported file is
        validated"""
        Subscriber.decrement_special_issues_to_receive()

    def export_special_issue_routage_file(self, file_path):
        """Create the file to send to routing service for special issues"""
        # TODO rename the method (use routing)
        # TODO set it as function for pylint :)
        exporter = RoutageExporter(file_path)
        exporter.do_export_special_issue()

    def get_subscription_count(self):
        """Get the subscriber counter to displays it on notification area"""
        return Subscriber.get_count()

    def save_subscriber_action(self, event):
        """Called by the edition panel to save the subscriber in database"""
        sub = {}
        for key in self.field_widget_dict.keys():
            sub[key] = self.field_widget_dict[key].GetValue()
        adapter = SubscriberAdapter(sub)
        self.subscriber_values = adapter.save_subscriber()
        self.frame.show_save_confirmation()

class SubscriberAdapter(object):
    """Adatpter to change a dict with subscriber values to a Subscriber
    object"""
    def __init__(self, subscriber_dict=None, db_sub=None):
        """Depending on parameter provided, the adapter initialize a dictionary
        or a Subscriber object"""
        if subscriber_dict is None:
            self.sub = {}
        else:
            self.sub = subscriber_dict

        if db_sub is None:
            self.db_sub = Subscriber()
        else:
            self.db_sub = db_sub

    def save_subscriber(self):
        """Save subscriber information in db and return the subscriber dict
        with generated new subscriber id"""
        self._set_naming_info()
        self._set_address_info()
        self._set_subscription_info()
        self._save_and_retrieve_id()
        return self.sub

    def _set_naming_info(self):
        """Sets the information on name, email, etc."""
        if self._is_defined('lastname'):
            self.db_sub.lastname = self.sub['lastname']
        if self._is_defined('firstname'):
            self.db_sub.firstname = self.sub['firstname']
        if self._is_defined('email_address'):
            self.db_sub.email_address = self.sub['email_address']
        if self._is_defined('company'):
            self.db_sub.company = self.sub['company']
        if self._is_defined('name_addition'):
            self.db_sub.name_addition = self.sub['name_addition']

    def _is_defined(self, field):
        """Return True if the field is defined in the dict and if it is not
        empty"""
        return \
                field in self.sub.keys() \
                and unicode(self.sub[field]).strip() != ''

    def _set_address_info(self):
        """Sets address information for the customer"""
        address = Address()
        if self._is_defined('address'):
            address.address1 = self.sub['address']
        if self._is_defined('address_addition'):
            address.address2 = self.sub['address_addition']
        if self._is_defined_and_int('post_code'):
            address.post_code = int(self.sub['post_code'])
        if self._is_defined('city'):
            address.city = self.sub['city']
        self.db_sub.address = address

    def _is_defined_and_int(self, field):
        """Check if the field is defined and if it is an int. My point is to
        avoid the use of an exception"""
        if self._is_defined(field):
            return unicode(self.sub[field]).strip().isdigit()
        else: return False

    def _set_subscription_info(self):
        """Sets the information about the subscription"""
        self._set_issues_info()
        self._set_pricing_info()
        self._set_date_info()
        self._set_misc_info()

    def _set_issues_info(self):
        """Sets the information about the issues to receive"""
        if self._is_defined_and_int('subscriber_since_issue'):
            self.db_sub.subscriber_since_issue = \
                    self.sub['subscriber_since_issue']
        if self._is_defined_and_int('issues_to_receive'):
            self.db_sub.issues_to_receive = \
                    self.sub['issues_to_receive']
        if self._is_defined_and_int('subs_beginning_issue'):
            self.db_sub.subs_beginning_issue = \
                    self.sub['subs_beginning_issue']
        if self._is_defined_and_int('hors_serie1'):
            self.db_sub.hors_serie1 = \
                    self.sub['hors_serie1']

    def _set_pricing_info(self):
        """Sets the information about subscription and membership pricing"""
        new_sub_price = \
            self._convert_field_to_float_str('subscription_price')
        new_membership_price = \
            self._convert_field_to_float_str('membership_price')
        
        try:
            self.db_sub.subscription_price = float(new_sub_price)
        except ValueError:
            self.db_sub.subscription_price = 0.0
            
        try:
            self.db_sub.membership_price = float(new_membership_price)
        except ValueError:
            self.db_sub.membership_price = 0.0

    def _convert_field_to_float_str(self, field_key):
        """Converts a french typed float string to a python float"""
        if self._is_defined(field_key):
            return self.sub[field_key].replace(',', '.')
        else:
            return '0'

    def _set_date_info(self):
        """Converts a French format date field (dd/mm/YYYY) to a python date"""
        if self._is_defined('subscription_date'):
            try:
                day, month, year = self.sub['subscription_date'].split('/')
                self.db_sub.subscription_date = date(
                        int(year),
                        int(month),
                        int(day)
                        )
            except ValueError:
                # We keep the default value, which is current date
                pass

    def _set_misc_info(self):
        """Sets the rest of the information for the subscriber"""
        if self._is_defined('ordering_type'):
            self.db_sub.ordering_type = \
                    self.sub['ordering_type']
        if self._is_defined('comment'):
            self.db_sub.comment = \
                    self.sub['comment']

    def _save_and_retrieve_id(self):
        """Save the subscriber in DB"""
        if self._is_defined('subscriber_id'):
            self.db_sub.identifier = self.sub['subscriber_id']
        self.db_sub.save()
        self.sub['subscriber_id'] = self.db_sub.identifier

    @classmethod
    def get_subscribers_from_lastname(cls, lastname):
        """Retrived a subscriber dict from the lastname"""
        sub_list = Subscriber.get_subscribers_from_lastname(lastname)
        return SubscriberAdapter._build_dict_list(sub_list)

    @classmethod
    def get_subscribers_from_company(cls, company):
        """Retrived a subscriber dict from the company"""
        sub_list = Subscriber.get_subscribers_from_company(company)
        return SubscriberAdapter._build_dict_list(sub_list)

    @classmethod
    def get_subscribers_from_email(cls, email):
        """Retrived a subscriber dict from the email"""
        sub_list = Subscriber.get_subscribers_from_email(email)
        return SubscriberAdapter._build_dict_list(sub_list)

    @classmethod
    def _build_dict_list(cls, sub_list):
        sub_dict_list = []
        for sub in sub_list:
            adapt = SubscriberAdapter(db_sub=sub)
            adapt.build_dict()
            sub_dict_list.append(adapt.sub)
        return sub_dict_list

    @classmethod
    def delete_from_id(cls, subscriber_id):
        """Delete a sbscriber from the db using provided id"""
        Subscriber.delete_from_id(subscriber_id)

    def build_dict(self):
        """Create the subscriber dictionary from the ASubscriber object"""
        # TODO break it down!
        self.sub = {
                'subscriber_id': self.db_sub.identifier,
                'lastname': self.db_sub.lastname,
                'firstname': self.db_sub.firstname,
                'email_address': self.db_sub.email_address,
                'name_addition': self.db_sub.name_addition,
                'company': self.db_sub.company
                }
        self._get_address_info()
        self.sub['subscription_date'] = self.db_sub \
                .subscription_date \
                .strftime('%d/%m/%Y')
        self.sub['issues_to_receive'] = str(self.db_sub.issues_to_receive)
        self.sub['subs_beginning_issue'] = str(self.db_sub.subs_beginning_issue)

        try:
            self.sub['subscription_price'] = \
                    ('%.2f' % self.db_sub.subscription_price) \
                    .replace('.', ',') 
        except TypeError:
            self.sub['subscription_price'] = '0,00'

        try:
            self.sub['membership_price'] = \
                    ('%.2f' % self.db_sub.membership_price) \
                    .replace('.', ',') 
        except TypeError:
            self.sub['membership_price'] = '0,00'

        self.sub['hors_serie1'] = str(self.db_sub.hors_serie1)
        self.sub['ordering_type'] = self.db_sub.ordering_type
        self.sub['comment'] = self.db_sub.comment
        
        return self.sub

    def _get_address_info(self):
        """Retrieve the address information from the Subscriber"""
        address = self.db_sub.address
        self.sub['address'] = address.address1
        self.sub['address_addition'] = address.address2
        if address.post_code != 0:
            self.sub['post_code'] = '%05d' % address.post_code
        else:
            self.sub['post_code'] = ''
        self.sub['city'] = address.city
