#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Object to manipulate a subscriber'''

import sqlite3
import os
import datetime
import gaabo_conf


class Subscriber(object):
    '''Object to manipulate a subscriber'''
    ISSUES_IN_A_YEAR = 6

    def __init__(self):
        '''First constructor to create a named subscriber'''
        self.identifier = -1
        self.lastname = '' 
        self.firstname = ''
        self.company = ''
        self.name_addition = ''
        self.address = Address()
        self.email_address = ''
        self.subscriber_since_issue = 0
        self.subscription_date = datetime.date.today()
        self.issues_to_receive = 0
        self.subs_beginning_issue = 0
        self.member = 0
        self.subscription_price = 0.0
        self.membership_price = 0.0
        self.hors_serie1 = 0
        self.hors_serie2 = 0
        self.hors_serie3 = 0
        self.sticker_sent = 0
        self.comment = ''
        self.bank = ''
        self.ordering_type  = ''
        self.dao = SubscriberDAO()

    def order_new_subscription(self):
        '''Add a new year of subscription to this subscriber'''
        self.issues_to_receive = self.issues_to_receive + self.ISSUES_IN_A_YEAR

    @classmethod
    def get_subscribers_from_lastname(cls, lastname):
        '''Returns a subscriber using the DAO'''
        adhoc_dao = SubscriberDAO()
        return adhoc_dao.search_from_lastname(lastname)

    @classmethod
    def get_subscribers_from_company(cls, company):
        adhoc_dao = SubscriberDAO()
        return adhoc_dao.search_from_company(company)

    @classmethod
    def get_subscribers_from_email(cls, email):
        adhoc_dao = SubscriberDAO()
        return adhoc_dao.search_from_email(email)

    @classmethod
    def decrement_issues_to_receive(cls):
        adhoc_dao = SubscriberDAO()
        adhoc_dao.decrement_issues_to_receive()

    @classmethod
    def decrement_special_issues_to_receive(cls):
        adhoc_dao = SubscriberDAO()
        adhoc_dao.decrement_special_issues_to_receive()

    @classmethod
    def get_end_of_subscribtion(cls):
        adhoc_dao = SubscriberDAO()
        return adhoc_dao.get_end_of_subscribtion()

    @classmethod
    def get_count(cls):
        adhoc_dao = SubscriberDAO()
        return adhoc_dao.get_count()

    @classmethod
    def delete_from_id(cls, identifier):
        """Delete a sbscriber from the db using provided id"""
        adhoc_dao = SubscriberDAO()
        adhoc_dao.delete(identifier)

    def save(self):
        if self.identifier == -1:
            self.dao.save(self)
            self.identifier = self.dao.get_new_subscriber_id()
        else:
            self.dao.update(self)

    def delete(self):
        self.dao.delete(self.identifier)

    def get_attribute_sequence(self):
        return (self.lastname, self.firstname, self.company,
                self.name_addition) + \
                self.address.to_tuple() + \
                (self.email_address,
                self.subscriber_since_issue, self.subscription_date,
                self.issues_to_receive, self.subs_beginning_issue,
                self.member, self.subscription_price, self.membership_price,
                self.hors_serie1, self.hors_serie2, self.hors_serie3,
                self.sticker_sent, self.comment, self.bank, self.ordering_type)

class Address(object):
    """Class that represent the subscriber address. It's a simple data
    structure"""
    def __init__(self):
        self.address1 = ''
        self.address2 = ''
        self.post_code = 0
        self.city = ''

    def to_tuple(self):
        return (self.address1, self.address2, self.post_code, self.city)

################################################################################

class SubscriberDAO(object):
    '''Data Access Object that acts with Subscribers from a DB'''

    def __init__(self):
        '''Initialise the dao with a database connection'''

        self.db_full_path = os.path.join(gaabo_conf.db_directory, gaabo_conf.db_name)
        self.conn = sqlite3.Connection(self.db_full_path)
        self.cursor = self.conn.cursor()

    def search_from_lastname(self, lastname):
        '''Return a list of subs from a search in the DB based on a lastname'''

        sql = """SELECT * FROM subscribers
        WHERE lower(lastname) LIKE lower(?)"""
        self.result = self.cursor.execute(sql, (lastname + '%', ))
        return self.fetch_result()

    def search_from_company(self, company):
        '''Return a list of subs from a search in the DB based on a company'''

        sql = """SELECT * FROM subscribers
        WHERE lower(company) LIKE lower(?)"""
        self.result = self.cursor.execute(sql, (company + '%', ))
        return self.fetch_result()

    def search_from_email(self, email):
        """Return a list of subscribers from a search in the DB based on the
        email address. *Warning:* only EXACT matches are returned"""

        sql = """SELECT * FROM subscribers WHERE lower(email_address) =
        lower(?)"""
        self.result = self.cursor.execute(sql, (email, ))
        return self.fetch_result()

    def get_new_subscriber_id(self):
        """Get the ID of last inserted subscriber"""
        sql = "SELECT seq FROM SQLITE_SEQUENCE WHERE name='subscribers'"
        for row in self.cursor.execute(sql):
            identifier = row[0]
        return identifier

    def fetch_result(self):
        '''Fetch class variable result into a list of Subscriber'''
        sublist = []
        for row in self.result:
            sub = Subscriber()
            address = Address()
            sub.identifier = row[0]
            sub.lastname = row[1]
            sub.firstname = row[2]
            sub.company = row[3]
            sub.name_addition = row[4]
            address.address1 = row[5]
            address.address2 = row[6]
            address.post_code = row[7]
            address.city = row[8]
            sub.email_address = row[9] 
            sub.subscriber_since_issue = row[10] 
            iso_date_string = row[11]
            sub.issues_to_receive = row[12] 
            sub.subs_beginning_issue = row[13] 
            sub.member = row[14] 
            sub.subscription_price = row[15] 
            sub.membership_price = row[16]
            sub.hors_serie1 = row[17]
            sub.sticker_sent = row[20]
            sub.comment = row[21]
            sub.ordering_type = row[23]
            
            sub.subscription_date = date_from_iso(iso_date_string)
            sub.address = address
            sublist.append(sub)
        return sublist


    def save(self, subscriber):
        sql = """INSERT INTO subscribers (
        lastname, firstname, company,
        name_addition, address, address_addition, post_code, city,
        email_address, subscriber_since_issue, subscription_date, issues_to_receive,
        subs_beginning_issue, member, subscription_price,
        membership_price, hors_serie1, hors_serie2, hors_serie3,
        sticker_sent, comment, bank, ordering_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(sql, subscriber.get_attribute_sequence())
        self.conn.commit()

    def update(self, subscriber):
        sql = """UPDATE subscribers
        SET
        lastname = ?,
        firstname = ?,
        company = ?,
        name_addition = ?,
        address = ?,
        address_addition = ?,
        post_code = ?,
        city = ?,
        email_address = ?,
        subscriber_since_issue = ?,
        subscription_date = ?,
        issues_to_receive = ?,
        subs_beginning_issue = ?,
        member = ?,
        subscription_price = ?,
        membership_price = ?,
        hors_serie1 = ?,
        hors_serie2 = ?,
        hors_serie3 = ?,
        sticker_sent = ?,
        comment = ?,
        bank = ?,
        ordering_type = ?
        WHERE id = ?
        """
        self.cursor.execute(
                sql,
                subscriber.get_attribute_sequence() +
                (subscriber.identifier,))
        self.conn.commit()

    def delete(self, identifier):
        sql = """DELETE FROM subscribers WHERE id = ?"""
        self.cursor.execute(sql, (identifier, ))
        self.conn.commit()
        
    def decrement_issues_to_receive(self):
        sql = """UPDATE subscribers
        SET issues_to_receive = issues_to_receive - 1
        WHERE issues_to_receive > 0"""
        self.cursor.execute(sql)
        self.conn.commit()

    def decrement_special_issues_to_receive(self):
        sql = """UPDATE subscribers
        SET hors_serie1 = hors_serie1 - 1
        WHERE hors_serie1 > 0"""
        self.cursor.execute(sql)
        self.conn.commit()

    def common_decrementor(self, field_name):
        pass

    def get_end_of_subscribtion(self):
        sql = """SELECT * FROM subscribers WHERE issues_to_receive < 2"""
        self.result = self.cursor.execute(sql)
        return self.fetch_result()

    def get_count(self):
        sql = """SELECT COUNT(*) FROM subscribers"""
        result = self.cursor.execute(sql)
        for row in result: return row[0]

# Module Functions
# TODO extract ! Subscriber does not care about this date stuff!

def date_from_iso(iso_date_string):
    default_date = datetime.date(1900, 01, 01)
    if iso_date_string is None:
        return default_date
    (year, month, day) = iso_date_string.split('-')
    if is_correct_date(year, month, day):
        return datetime.date(int(year), int(month), int(day))
    else:
        return default_date

def is_correct_date(year, month, day):
    # TODO this can be reused in the UI
    """Show is the year can be transforme to a datetime.date and formatted"""

    if cannot_be_formatted(year):
        return False
    elif cannot_create_date(year, month, day):
        return False
    else:
        return True

def cannot_be_formatted(year):
    """Years bellow 1900 cannot be formatted by strftime"""
    if str(year).isdigit() and int(year) < 1900:
        return True
    else:
        return False

def cannot_create_date(year, month, day):
    """Try to create a date to check that the params are correct"""
    try:
        datetime.date(int(year), int(month), int(day))
        return False
    except:
        return True

