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
    """This object allows to bulk insert data in the subscriber database from a
    plain file."""

    def __init__(self, file_full_path):
        """Creates file object to parse and import"""
        self.current_line = 1
        self.imported_lines_counter = 0

        self.imported_file = codecs.open(file_full_path, 'rb', 'utf-8')
        #first line is considered as header and skipped
        self.imported_file.readline()

        log_dir = gaabo_conf.log_directory
        self.bad_file = codecs.open(
                os.path.join(log_dir, 'SubscriberImporter.bad'),
                'w',
                'utf-8')
        self.logger = FileLogger(
                'SubscriberImporter',
                os.path.join(log_dir, 'SubscriberImporter.log')
                )
        self.line = ''
        self.sub = None 
        self.splitted_line = []

    def do_truncate_import(self):
        """Creates subscriber object from file and save them in the database"""
        db_operator = SqliteDbOperator()
        db_operator.create_db()
        self.__do_common_import()

    def do_append_import(self):
        """Perform an import from self.imported_file without altering existing
        data."""
        self.__do_common_import()

    def do_update_import(self):
        """Perform an import from self.imported_file. Existing entries are
        updated. The search of existing is the email address which should be
        unique if it is set. If two emails are found we keep the first. If no
        email is found, en error message is put in the log and a new subscriber
        is created."""
        for self.line in self.imported_file:
            self.current_line+= 1

            if len(self.line.strip()) > 0:
                self.splitted_line = self.line.rstrip('\n').split('\t')
                email = self.splitted_line[20].lower()
                subs_list = []
                if email:
                    subs_list = Subscriber.get_subscribers_from_email(email)
                else:
                    message = (
                            u"L'abonné ligne %d n'a pas d'adresse email : "
                            + u"il sera créé en base."
                            )
                    self.logger.info(message % self.current_line)
                    
                self.__get_sub_from_retieved(subs_list, email)
                self.__extract_subscriber()
                self.sub.save()
                self.imported_lines_counter += 1
        self.logger.info('%d lignes importées' % self.imported_lines_counter)
        self.bad_file.close()

    def __get_sub_from_retieved(self, retrieved_list, email):
        """Generate a Sbuscriber from the result of db search."""
        # TODO virer l'email et faire un throw d'exception
        self.sub = None
        if len(retrieved_list) == 0:
            self.sub = Subscriber()
        elif len(retrieved_list) == 1:
            self.sub = retrieved_list[0]
        elif len(retrieved_list) > 1:
            self.sub = retrieved_list[0]
            message = (
                    u"L'adresse email %s est trouvée plus d'une "
                    + u"fois dans la base. Ligne %d."
            )
            self.logger.error(message % (email, self.current_line))
        return self.sub

    def __do_common_import(self):
        """Common method to import data from self.imported_file"""
        self.sub = Subscriber()

        for self.line in self.imported_file:
            self.current_line += 1
            if len(self.line.strip()) > 0:
                self.splitted_line = self.line.rstrip('\n').split('\t')
                self.sub.identifier = -1
                self.__extract_subscriber()
                self.sub.save()
                self.imported_lines_counter += 1
        self.logger.info('%d lignes importées' % self.imported_lines_counter)
        self.bad_file.close()

    def __extract_subscriber(self):
        """Build a Subscriber object from the information of a line"""

        # The same subscriber object is used, but it must be reinitialized
        self.__set_personal_information()
        self.__set_subscription_info()
        self.__set_ordering_info()
        self.__set_membership_info()
        self.__set_miscelaneous_info()

    def __set_personal_information(self):
        """Put info like name and address in the Subscriber"""
        self.sub.lastname = self.splitted_line[9]
        self.sub.firstname = self.splitted_line[10]
        self.sub.email_address = self.splitted_line[20].lower()
        self.sub.company = self.splitted_line[11]
        self.sub.name_addition = self.splitted_line[12]
        self.sub.address = self.splitted_line[13]
        self.sub.address_addition = self.splitted_line[14]
        self.sub.post_code = self.__field_to_int(self.splitted_line[15], 'post_code')
        self.sub.city = self.splitted_line[16]

    def __set_subscription_info(self):
        """Put the info about running subscription in the Subscriber"""
        self.sub.subscription_date = extract_date(
                self.splitted_line[0]
                )
        self.sub.issues_to_receive = self.splitted_line[1]
        self.sub.subs_beginning_issue = self.__field_to_int(
                self.splitted_line[2],
                'subs_beginning_issue'
                )
        self.sub.subscriber_since_issue = self.__format_sub_since_issue(
                self.splitted_line[21],
                self.sub.subs_beginning_issue
                )
        self.sub.hors_serie1 = self.__field_to_int(
                self.splitted_line[3], 'hors_serie1'
                )

    def __field_to_int(self, field, field_name):
        """Process a field that is expected to be an int"""
        if field.strip() == '':
            returned_field = 0
        else:
            try:
                returned_field = int(field)
            except(ValueError):
                returned_field = 0
                error_params = ('int', field, field_name)
                self.__show_bad_field_error(error_params)
        return returned_field

    def __show_bad_field_error(self, param_tuple):
        """Log and error when bad field information is found"""
        field_type, field, field_name = param_tuple 
        self.logger.error( 
                ' wrong value %s for field %s line %d: %s expected.\n'
                % (field, field_name, self.current_line, field_type)
                )
        self.__print_bad_line()

    def __print_bad_line(self):
        '''Print current line in the bad file'''
        # TODO rather than propagate bad line, throw an exception to
        # __do_common_import
        self.bad_file.write(self.line)

    def __format_sub_since_issue(self, field, beginning_issue):
        """Set a right int value in subscriber since issue field"""
        subscriber_since_issue = field
        if subscriber_since_issue.lower() == 'oui': 
            return beginning_issue - 6
        else:
            returned_value = self.__field_to_int(
                    subscriber_since_issue,
                    'subscriber_since_issue'
                    )
            return returned_value

    def __set_ordering_info(self):
        """Put financial information into Subscriber object"""
        self.sub.ordering_type = self.splitted_line[7].lower()
        self.sub.subscription_price = self.splitted_line[17]
        self.sub.bank = self.splitted_line[8]
        self.sub.membership_price = self.__field_to_float(
                self.splitted_line[18],
                'membership_price'
                )

    def __field_to_float(self, field, field_name):
        '''Process a field that is expected to be an float'''
        if field.strip() == '':
            return 0.0
        else:
            try:
                formated_field = field.replace(',', '.')
                return float(formated_field)
            except(ValueError):
                error_params = ('float', field, field_name)
                self.__show_bad_field_error(error_params)
                return 0.0

    def __set_membership_info(self):
        """Put information about association membership in Subscriber object"""
        member = self.splitted_line[6]
        if member.lower() == 'oui':
            self.sub.member = 1
        else:
            self.sub.member = 0

    def __set_miscelaneous_info(self):
        """Put information belonging to no defined category into Subscriber
        object"""
        self.sub.sticker_sent = self.__field_to_int(
                self.splitted_line[23],
                'sticker_sent'
                )
        self.sub.comment = self.splitted_line[19]

###
# Common functions
###

def extract_date(date_string):
    """Extract a date object from a string with field separated by /"""
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
