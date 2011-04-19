#!/usr/bin/env python
'''
This module contains a controler to make gaabo works
'''

from subscriber import Subscriber
from subscriber_exporter import RoutageExporter

class Controler(object):
    def __init__(self):
        pass

    def get_searched_customer_list(self, lastname, company):
        subs_list = [] 
        if lastname:
            subs_list.extend(Subscriber.get_subscribers_from_lastname(lastname))
        if company:
            subs_list.extend(Subscriber.get_subscribers_from_company(company))
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

    def get_ending_subscription_list(self):
        output = []
        for subscriber in Subscriber.get_end_of_subscribtion():
            output.append('\t'.join((
                subscriber.lastname,
                subscriber.firstname,
                subscriber.company,
                subscriber.email_address,
                '%d numero a recevoir' % subscriber.issues_to_receive
                ))) 
        return output

