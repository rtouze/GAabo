#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Module to import subscribers form a file extracted from excel'''
from subscriber import Subscriber
from gaabo_logger import FileLogger
from gaabo_exploit_db import SqliteDbOperator
import gaabo_conf
import datetime
import codecs
import os


class SubscriberImporter(object):
    def __init__(self, file_full_path):
        '''Creates file object to parse and import'''
        self.imported_file = codecs.open(file_full_path, 'rb', 'utf-8')
        log_dir = gaabo_conf.log_directory
        self.bad_file = codecs.open(
                os.path.join(log_dir, 'SubscriberImporter.bad'),
                'w',
                'utf-8')
        self.logger = FileLogger(
                'SubscriberImporter',
                os.path.join(log_dir, 'SubscriberImporter.log')
                )
        self.db_operator = SqliteDbOperator()

    def do_truncate_import(self):
        '''Creates subscriber object from file and save them in the database'''
        #first line is skiped
        self.db_operator.create_db()
        self.current_line = 1
        self.imported_file.readline()
        self.sub = Subscriber()
        for self.line in self.imported_file:
            if len(self.line.strip()) > 0:
                self.current_line += 1
                self.extract_subscriber()
                self.sub.save()
        self.logger.info('%d lignes importees' % self.current_line)
        self.bad_file.close()

    def create_db(self):
        gaabo_exploit_db.create_db()

    def extract_subscriber(self):
        '''Build a Subscriber object from the information of a line'''

        splitted_line = self.line.rstrip('\n').split('\t')
        self.sub.lastname = splitted_line[9]
        self.sub.firstname = splitted_line[10]
        self.sub.company = splitted_line[11]
        self.sub.name_addition = splitted_line[12]
        self.sub.subscription_date = self.extract_date(
                splitted_line[0]
                )
        self.sub.issues_to_receive = splitted_line[1]
        self.sub.subs_beginning_issue = self.field_to_int(splitted_line[2], 'subs_beginning_issue')
        self.sub.ordering_type = splitted_line[7].lower()
        self.sub.address = splitted_line[13]
        self.sub.post_code = splitted_line[15]
        self.sub.city = splitted_line[16]
        self.sub.subscription_price = splitted_line[17]
        self.sub.membership_price = self.field_to_int(splitted_line[18], 'membership_price')
        self.sub.email_address = splitted_line[20].lower()
        self.sub.subscriber_since_issue = self.format_sub_since_issue(
                splitted_line[21],
                self.sub.subs_beginning_issue
                )

        self.sub.sticker_sent = self.field_to_int(splitted_line[23], 'sticker_sent')
        self.sub.comment = splitted_line[19]
        self.sub.bank = splitted_line[8]
        self.sub.address_addition = splitted_line[14]
        self.sub.hors_serie1 = self.field_to_int(splitted_line[3], 'hors_serie1')
        self.sub.hors_serie2 = self.field_to_int(splitted_line[4], 'hors_serie2')
        self.sub.hors_serie3 = self.field_to_int(splitted_line[5], 'hors_serie3')

        member = splitted_line[6]
        if member.lower() == 'oui':
            self.sub.member = 1
        else:
            self.sub.member = 0

    def format_sub_since_issue(self, field, beginning_issue):
        '''Set a right int value in subscriber since issue field'''
        subscriber_since_issue = field
        if subscriber_since_issue.lower() == 'oui': 
            return beginning_issue - 6
        else:
            return self.field_to_int(subscriber_since_issue, 'subscriber_since_issue')


    def field_to_int(self, field, field_name):
        '''Process a field that is expected to be an int'''
        if field.strip() == '':
            returned_field = 0
        else:
            try:
                returned_field = int(field)
            except(ValueError):
                returned_field = 0
                self.logger.error( 
                        ' wrong value %s for field %s line %d: integer expected.\n'
                        % (field, field_name, self.current_line)
                        )
                self.print_bad_line()
        return returned_field

    def print_bad_line(self):
        '''Print current line in the bad file'''
        self.bad_file.write(self.line)

    #TODO gerer les IndexError: list index out of range
    def extract_date(self, date_string):
        '''Extract a date object from a string with field separated by /'''
        splitted_date = date_string.split('/')
        try:
            my_date = datetime.date(
                    int(splitted_date[2]),
                    int(splitted_date[1]),
                    int(splitted_date[0])
                    )
        except(IndexError):
            my_date = datetime.date.today()
        return my_date
