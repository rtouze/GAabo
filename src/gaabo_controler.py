#!/usr/bin/env python
"""This module contains a controler to make gaabo works"""

__author__ = 'romain.touze@gmail.com'

from datetime import date
from subscriber import Subscriber
from subscriber import Address
from subscriber_exporter import RoutageExporter

class Controler(object):
    def __init__(self, frame):
        self.subscriber_values = {}
        self.field_widget_dict = {}
        self.frame = frame

    def get_searched_customer_list(self, lastname, company, email):
        subs_list = [] 
        if lastname:
            subs_list.extend(SubscriberAdapter.get_subscribers_from_lastname(lastname))
        if company:
            subs_list.extend(SubscriberAdapter.get_subscribers_from_company(company))
        if email:
            subs_list.extend(SubscriberAdapter.get_subscribers_from_email(email))

        identifiers = []
        index = 0
        for subscriber in subs_list:
            if subscriber['subscriber_id'] in identifiers:
                subs_list.pop(index)
            else:
                identifiers.append(subscriber['subscriber_id'])
            index += 1
        
        return subs_list

    def delete_subscriber(self, subscriber):
        # TODO - modify
        subscriber.delete()

    def export_regular_issue_routage_file(self, file_path):
        exporter = RoutageExporter(file_path)
        exporter.do_export()

    def decrement_normal_issues_to_receive(self):
        Subscriber.decrement_issues_to_receive()

    def decrement_special_issues_to_receive(self):
        Subscriber.decrement_special_issues_to_receive()

    def export_special_issue_routage_file(self, file_path):
        exporter = RoutageExporter(file_path)
        exporter.do_export_special_issue()

    def get_subscription_count(self):
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
        print 'DEBUG - saved ' + str(self.sub)
        return self.sub

    def _set_naming_info(self):
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
        return \
                field in self.sub.keys() \
                and unicode(self.sub[field]).strip() != ''

    def _set_address_info(self):
        address = Address()
        if self._is_defined('address'):
            address.address1 = self.sub['address']
        if self._is_defined('address_addition'):
            address.address2 = self.sub['address_addition']
        if self._is_defined('post_code'):
            # TODO check that it's an int
            address.post_code = int(self.sub['post_code'])
        if self._is_defined('city'):
            address.city = self.sub['city']
        self.db_sub.address = address

    def _set_subscription_info(self):
        self._set_issues_info()
        self._set_pricing_info()
        self._set_date_info()
        self._set_misc_info()

    def _set_issues_info(self):
        # TODO check numbers
        if self._is_defined('subscriber_since_issue'):
            self.db_sub.subscriber_since_issue = \
                    self.sub['subscriber_since_issue']
        if self._is_defined('issues_to_receive'):
            self.db_sub.issues_to_receive = \
                    self.sub['issues_to_receive']
        if self._is_defined('subs_beginning_issue'):
            self.db_sub.subs_beginning_issue = \
                    self.sub['subs_beginning_issue']
        if self._is_defined('hors_serie1'):
            self.db_sub.hors_serie1 = \
                    self.sub['hors_serie1']

    def _set_pricing_info(self):
        # TODO check floats
        if self._is_defined('subscription_price'):
            self.db_sub.subscription_price = \
                    float(self.sub['subscription_price'].replace(',', '.'))
        if self._is_defined('membership_price'):
            self.db_sub.membership_price = \
                    float(self.sub['membership_price'].replace(',', '.'))

    def _set_date_info(self):
        # TODO check date
        if self._is_defined('subscription_date'):
            day, month, year = self.sub['subscription_date'].split('/')
            self.db_sub.subscription_date = date(
                    int(year),
                    int(month),
                    int(day)
                    )

    def _set_misc_info(self):
        if self._is_defined('ordering_type'):
            self.db_sub.ordering_type = \
                    self.sub['ordering_type']
        if self._is_defined('comment'):
            self.db_sub.comment = \
                    self.sub['comment']

    def _save_and_retrieve_id(self):
        if self._is_defined('subscriber_id'):
            self.db_sub.identifier = self.sub['subscriber_id']
        self.db_sub.save()
        self.sub['subscriber_id'] = self.db_sub.identifier

    @classmethod
    def get_subscribers_from_lastname(cls, lastname):
        sub_list = Subscriber.get_subscribers_from_lastname(lastname)
        return SubscriberAdapter._build_dict_list(sub_list)

    @classmethod
    def get_subscribers_from_company(cls, company):
        sub_list = Subscriber.get_subscribers_from_company(company)
        return SubscriberAdapter._build_dict_list(sub_list)

    @classmethod
    def get_subscribers_from_email(cls, email):
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

    def build_dict(self):
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
        self.sub['subscription_price'] = \
                ('%.2f' % self.db_sub.subscription_price) \
                .replace('.', ',') 
        self.sub['membership_price'] = \
                ('%.2f' % self.db_sub.membership_price) \
                .replace('.', ',') 
        self.sub['hors_serie1'] = str(self.db_sub.hors_serie1)
        self.sub['ordering_type'] = self.db_sub.ordering_type
        self.sub['comment'] = self.db_sub.comment
        
        return self.sub

    def _get_address_info(self):
        address = self.db_sub.address
        self.sub['address'] = address.address1
        self.sub['address_addition'] = address.address2
        self.sub['post_code'] = '%05d' % address.post_code
        self.sub['city'] = address.city

        
