#!/usr/bin/env python
"""This module contains a controler to make gaabo works"""

__author__ = 'romain.touze@gmail.com'

from subscriber import Subscriber
from subscriber_exporter import RoutageExporter

class Controler(object):
    def __init__(self):
        self.subscriber_values = {}
        self.field_widget_dict = {}

    def get_searched_customer_list(self, lastname, company, email):
        subs_list = [] 
        if lastname:
            subs_list.extend(Subscriber.get_subscribers_from_lastname(lastname))
        if company:
            subs_list.extend(Subscriber.get_subscribers_from_company(company))
        if email:
            subs_list.extend(Subscriber.get_subscribers_from_email(email))

        identifiers = []
        index = 0
        for subscriber in subs_list:
            if subscriber.identifier in identifiers:
                subs_list.pop(index)
            else:
                identifiers.append(subscriber.identifier)
            index += 1
        
        return subs_list

    def delete_subscriber(self, subscriber):
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

class SubscriberAdapter(object):
    """Adatpter to change a dict with subscriber values to a Subscriber
    object"""
    def __init__(self, subscriber_dict):
        self.sub = subscriber_dict
    def save_subscriber(self):
        subscriber = Subscriber()
        subscriber.lastname = self.sub['lastname']
        subscriber.firstname = self.sub['firstname']
        subscriber.email_address = self.sub['email_address']
        subscriber.save()
        self.sub['subscriber_id'] = subscriber.identifier
        return self.sub
