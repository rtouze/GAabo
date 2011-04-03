#!/usr/bin/env python
'''This module tests the subscriber object'''

import unittest
from subscriber import Subscriber
import sqlite3
import gaabo_conf
import datetime

class TestSubscrisber(unittest.TestCase):
    '''Tests the Subscriber class'''

    def setUp(self):
        '''Initialize the object and database'''
        gaabo_conf.db_name = 'test.db'
        self.sub = Subscriber()
        self.conn = sqlite3.Connection('../databases/test.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('DELETE FROM subscribers')
        self.conn.commit()

    def tearDown(self):
        '''Close the database'''
        self.cursor.close()
        self.conn.close()

    def test_subscriber_last_name(self):
        '''Test if the subscriber is created with default values'''
        self.assertEquals(self.sub.lastname, '')
        self.assertEquals(self.sub.issues_to_receive, 6)

    def test_new_subscribtion(self):
        '''Test if the order_new_subscription method add 6 issues left'''
        former_issues_left = 3
        self.sub.issues_to_receive = former_issues_left
        self.sub.order_new_subscription()
        self.assertEquals(self.sub.issues_to_receive, former_issues_left + 6)

    def test_get_subscribers_from_name(self):
        '''Retrieve a subsriber list using name'''
        sql = """INSERT INTO subscribers (lastname, firstname)
        VALUES ('DUPONT', 'Jean')"""
        self.cursor.execute(sql)
        self.conn.commit()
        sub_class = Subscriber
        self.sub = sub_class.get_subscribers_from_lastname('DUPONT')[0]
        self.assertEquals(self.sub.firstname, 'Jean')

    def test_get_subscribers_from_company(self):
        '''Retrieve a subsriber list company name'''
        sql = """INSERT INTO subscribers (company, name_addition)
        VALUES ('Google', 'IsNotEvil')"""
        self.cursor.execute(sql)
        self.conn.commit()
        sub_class = Subscriber
        self.sub = sub_class.get_subscribers_from_company('Google')[0]
        self.assertEquals(self.sub.name_addition, 'IsNotEvil')

    def test_save_subscriber(self):
        '''Test that subscriber information are saved in the DB'''
        self.sub.firstname = 'John'
        self.sub.lastname = 'Doe'
        #TODO add other attributes
        self.sub.save()
        results = self.cursor.execute('SELECT firstname, lastname FROM subscribers')
        for row in results:
            self.assertEquals(row[0], 'John')
            self.assertEquals(row[1], 'Doe')

    def test_update_subscriber(self):
        '''Test that a subscriber update is well commited in the data base'''
        sql = """INSERT INTO subscribers (lastname, firstname)
        VALUES ('DUPONT', 'Jean')"""
        self.cursor.execute(sql)
        sql = """INSERT INTO subscribers (lastname, firstname)
        VALUES ('DUPONT', 'Jean')"""
        self.cursor.execute(sql)
        self.conn.commit()
        sub_class = Subscriber
        self.sub = sub_class.get_subscribers_from_lastname('DUPONT')[0]
        expected = 'jean.dupont@provider.net'
        self.sub.email_address = expected
        self.sub.save()
        sql = """SELECT email_address FROM subscribers
        WHERE lastname = 'DUPONT' AND id = ?"""
        result = self.cursor.execute(sql, (self.sub.identifier,))
        for row in result:
            actual = row[0]
        self.assertEquals(expected, actual)

    def test_delete_customer(self):
        '''Test if a given customer is deleted'''
        sql = """INSERT INTO subscribers (lastname, firstname)
        VALUES ('CANNE', 'Henri')"""
        self.cursor.execute(sql)
        self.conn.commit()
        sub_class = Subscriber
        self.sub = sub_class.get_subscribers_from_lastname('CANNE')[0]
        self.sub.delete()
        sql = """SELECT COUNT(1) FROM subscribers WHERE lastname = 'CANNE'"""
        result = self.cursor.execute(sql)
        for row in result:
            actual = row[0]
        expected = 0
        self.assertEquals(expected, actual)

    def test_decrement_issues_to_receive(self):
        self.sub.lastname = 'toto'
        self.sub.save()
        self.sub.lastname = 'tata'
        self.sub.save()
        self.sub.lastname = 'titi'
        self.sub.issues_to_receive = 0
        self.sub.save()
        Subscriber.decrement_issues_to_receive()
        sub = Subscriber.get_subscribers_from_lastname('toto')[0]
        self.assertEquals(sub.issues_to_receive, sub.ISSUES_IN_A_YEAR - 1)
        sub = Subscriber.get_subscribers_from_lastname('tata')[0]
        self.assertEquals(sub.issues_to_receive, sub.ISSUES_IN_A_YEAR - 1)
        sub = Subscriber.get_subscribers_from_lastname('titi')[0]
        self.assertEquals(sub.issues_to_receive, 0)

    def test_decrement_special_issues_to_receive(self):
        self.sub.lastname = 'toto'
        self.sub.hors_serie1 = 3
        self.sub.save()
        self.sub.lastname = 'tata'
        self.sub.hors_serie1 = 4
        self.sub.save()
        self.sub.lastname = 'titi'
        self.sub.hors_serie1 = 0
        self.sub.save()
        Subscriber.decrement_special_issues_to_receive()
        sub = Subscriber.get_subscribers_from_lastname('toto')[0]
        self.assertEquals(sub.hors_serie1, 2)
        sub = Subscriber.get_subscribers_from_lastname('tata')[0]
        self.assertEquals(sub.hors_serie1, 3)
        sub = Subscriber.get_subscribers_from_lastname('titi')[0]
        self.assertEquals(sub.hors_serie1, 0)

    def test_end_of_subscribtion_list(self):
        self.sub.lastname = 'toto'
        self.sub.issues_to_receive = 1
        self.sub.save()
        self.sub.lastname = 'tata'
        self.sub.issues_to_receive = 0
        self.sub.save()
        self.sub.lastname = 'titi'
        self.sub.issues_to_receive = 10
        self.sub.save()
        ending_sub_list = Subscriber.get_end_of_subscribtion()
        self.assertEquals(len(ending_sub_list), 2)
        self.assertEquals(ending_sub_list[0].lastname, 'toto')
        self.assertEquals(ending_sub_list[1].lastname, 'tata')

    def test_date(self):
        """Test the format of the date retrieved from the DB"""
        self.sub.lastname = 'toto'
        self.sub.subscription_date = datetime.date(2011, 3, 31)
        self.sub.save()
        sub = Subscriber.get_subscribers_from_lastname('toto')[0]
        actual_date = sub.subscription_date

        self.assertEquals(actual_date.strftime('%d/%m/%Y'), '31/03/2011')

if __name__ == '__main__':
    unittest.main()
