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
        self.address = ''
        self.address_addition = ''
        self.post_code = 0
        self.city = ''
        self.email_address = ''
        self.subscriber_since_issue = 0
        self.subscription_date = datetime.date.today()
        self.issues_to_receive = self.ISSUES_IN_A_YEAR
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


    def save(self):
        if self.identifier == -1:
            self.dao.save(self)
        else:
            self.dao.update(self)

    def delete(self):
        self.dao.delete(self.identifier)

    def get_attribute_sequence(self):
        return (self.lastname, self.firstname, self.company,
                self.name_addition, self.address, self.address_addition,
                self.post_code, self.city, self.email_address,
                self.subscriber_since_issue, self.subscription_date,
                self.issues_to_receive, self.subs_beginning_issue,
                self.member, self.subscription_price, self.membership_price,
                self.hors_serie1, self.hors_serie2, self.hors_serie3,
                self.sticker_sent, self.comment, self.bank, self.ordering_type)

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
        WHERE lower(lastname) = lower(?)"""
        self.result = self.cursor.execute(sql, (lastname, ))
        return self.fetch_result()

    def search_from_company(self, company):
        '''Return a list of subs from a search in the DB based on a company'''
        sql = """SELECT * FROM subscribers
        WHERE lower(company) = lower(?)"""
        self.result = self.cursor.execute(sql, (company, ))
        return self.fetch_result()

    def fetch_result(self):
        '''Fetch class variable result into a list of Subscriber'''
        sublist = []
        for row in self.result:
            sub = Subscriber()
            (sub.identifier, 
            sub.lastname, 
            sub.firstname, 
            sub.company, 
            sub.name_addition, 
            sub.address, 
            sub.address_addition, 
            sub.post_code, 
            sub.city, 
            sub.email_address, 
            sub.subscriber_since_issue, 
            iso_date_string,
            sub.issues_to_receive, 
            sub.subs_beginning_issue, 
            sub.member, 
            sub.subscription_price, 
            sub.membership_price,
            sub.hors_serie1,
            sub.hors_serie2,
            sub.hors_serie3,
            sub.sticker_sent,
            sub.comment,
            sub.bank,
            sub.ordering_type
            ) = row
            sub.subscription_date = self.date_from_iso(iso_date_string)
            sublist.append(sub)
        return sublist

    def date_from_iso(self, iso_date_string):
        if iso_date_string is not None:
            (year, month, day) = iso_date_string.split('-')
            return datetime.date(int(year), int(month), int(day))
        else:
            return None


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

