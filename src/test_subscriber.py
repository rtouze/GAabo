#!/usr/bin/env python
'''This module tests the subscriber object'''

import unittest
import sqlite3
import datetime

from subscriber import Subscriber
from subscriber import is_correct_date
import gaabo_conf

class TestSubscriber(unittest.TestCase):
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
        self.assertEqual(self.sub.lastname, '')
        self.assertEqual(self.sub.issues_to_receive, 6)

    def test_new_subscribtion(self):
        '''Test if the order_new_subscription method add 6 issues left'''
        former_issues_left = 3
        self.sub.issues_to_receive = former_issues_left
        self.sub.order_new_subscription()
        self.assertEqual(self.sub.issues_to_receive, former_issues_left + 6)

    def test_get_subscribers_from_name(self):
        '''Retrieve a subsriber list using name'''
        sql = """INSERT INTO subscribers (lastname, firstname)
        VALUES ('DUPONT', 'Jean')"""
        self.cursor.execute(sql)
        self.conn.commit()
        sub_class = Subscriber
        self.sub = sub_class.get_subscribers_from_lastname('DUPONT')[0]
        self.assertEqual(self.sub.firstname, 'Jean')

    def test_get_subscribers_from_name_like(self):
        '''Retrieve a subsriber list using beginning of the name'''
        sql = """INSERT INTO subscribers (lastname, firstname)
        VALUES ('DUPONT-ANDRE', 'Toto')"""
        self.cursor.execute(sql)
        self.conn.commit()
        sub_class = Subscriber
        self.sub = sub_class.get_subscribers_from_lastname('DUPONT')[0]
        self.assertEqual(self.sub.firstname, 'Toto')

    def test_get_subscribers_from_company(self):
        '''Retrieve a subsriber list using a company name'''
        sql = """INSERT INTO subscribers (company, name_addition)
        VALUES ('Google', 'IsNotEvil')"""
        self.cursor.execute(sql)
        self.conn.commit()
        sub_class = Subscriber
        self.sub = sub_class.get_subscribers_from_company('Google')[0]
        self.assertEqual(self.sub.name_addition, 'IsNotEvil')

    def test_get_subscribers_from_company_like(self):
        '''Retrieve a subsriber list using the beginning of company name'''
        sql = """INSERT INTO subscribers (company, name_addition)
        VALUES ('REDHAT', 'IsTrankil')"""
        self.cursor.execute(sql)
        self.conn.commit()
        sub_class = Subscriber
        self.sub = sub_class.get_subscribers_from_company('RED')[0]
        self.assertEqual(self.sub.name_addition, 'IsTrankil')

    def test_save_subscriber(self):
        '''Test that subscriber information are saved in the DB'''
        self.sub.firstname = 'John'
        self.sub.lastname = 'Doe'
        #TODO add other attributes
        self.sub.save()
        results = self.cursor.execute('SELECT firstname, lastname FROM subscribers')
        for row in results:
            self.assertEqual(row[0], 'John')
            self.assertEqual(row[1], 'Doe')

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
        self.assertEqual(expected, actual)

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
        self.assertEqual(expected, actual)

    def test_decrement_issues_to_receive(self):
        self.sub.lastname = 'toto'
        self.sub.save()
        self.sub = Subscriber()
        self.sub.lastname = 'tata'
        self.sub.save()
        self.sub = Subscriber()
        self.sub.lastname = 'titi'
        self.sub.issues_to_receive = 0
        self.sub.save()
        Subscriber.decrement_issues_to_receive()
        sub = Subscriber.get_subscribers_from_lastname('toto')[0]
        self.assertEqual(sub.issues_to_receive, sub.ISSUES_IN_A_YEAR - 1)
        sub = Subscriber.get_subscribers_from_lastname('tata')[0]
        self.assertEqual(sub.issues_to_receive, sub.ISSUES_IN_A_YEAR - 1)
        sub = Subscriber.get_subscribers_from_lastname('titi')[0]
        self.assertEqual(sub.issues_to_receive, 0)

    def test_decrement_special_issues_to_receive(self):
        self.sub.lastname = 'toto'
        self.sub.hors_serie1 = 3
        self.sub.save()
        self.sub = Subscriber()
        self.sub.lastname = 'tata'
        self.sub.hors_serie1 = 4
        self.sub.save()
        self.sub = Subscriber()
        self.sub.lastname = 'titi'
        self.sub.hors_serie1 = 0
        self.sub.save()
        Subscriber.decrement_special_issues_to_receive()
        sub = Subscriber.get_subscribers_from_lastname('toto')[0]
        self.assertEqual(sub.hors_serie1, 2)
        sub = Subscriber.get_subscribers_from_lastname('tata')[0]
        self.assertEqual(sub.hors_serie1, 3)
        sub = Subscriber.get_subscribers_from_lastname('titi')[0]
        self.assertEqual(sub.hors_serie1, 0)

    def test_end_of_subscribtion_list(self):
        self.sub.lastname = 'toto'
        self.sub.issues_to_receive = 1
        self.sub.save()
        self.sub = Subscriber()
        self.sub.lastname = 'tata'
        self.sub.issues_to_receive = 0
        self.sub.save()
        self.sub = Subscriber()
        self.sub.lastname = 'titi'
        self.sub.issues_to_receive = 10
        self.sub.save()
        ending_sub_list = Subscriber.get_end_of_subscribtion()
        self.assertEqual(len(ending_sub_list), 2)
        self.assertEqual(ending_sub_list[0].lastname, 'toto')
        self.assertEqual(ending_sub_list[1].lastname, 'tata')

    def test_date(self):
        """Test the format of the date retrieved from the DB"""
        self.sub.lastname = 'toto'
        self.sub.subscription_date = datetime.date(2011, 3, 31)
        self.sub.save()
        sub = Subscriber.get_subscribers_from_lastname('toto')[0]
        actual_date = sub.subscription_date
        self.assertEqual(actual_date.strftime('%d/%m/%Y'), '31/03/2011')

    def test_wrong_date(self):
        """Test what appens when we store a wrong date in the db and try to
        format it"""
        self.sub.lastname = 'toto'
        self.sub.subscription_date = datetime.date(211, 7, 31)
        self.sub.save()
        sub = Subscriber.get_subscribers_from_lastname('toto')[0]
        actual_date = sub.subscription_date
        # When the date is false, we choose to display 01/01/1900...
        # A check must be done while typing the date in the UI to be sure it
        # won't happen
        #self.assertEqual(actual_date.strftime('%d/%m/%Y'), '01/01/1900')



    def test_new_subscriber_id(self):
        """Test if we can get the ID of a saved Subscriber"""
        self.sub.lastname='toto'
        self.sub.fistname='hero'
        self.sub.save()
        ident = self.sub.identifier
        self.assertNotEqual(-1, ident)

    def test_email_based_search(self):
        """Test if we can retrieve a subscriber using its email address."""
        self.sub.firstname = 'email'
        self.sub.lastname = 'user'
        email = 'email.user@foobar.com'
        self.sub.email_address = email
        self.sub.save()

        user = Subscriber.get_subscribers_from_email(email)[0]
        self.assertEqual(user.firstname, 'email')
        self.assertEqual(user.lastname, 'user')

class CorrectDateTest(unittest.TestCase):
    """This class tests if the function correct_date in module subscriber works
    well."""
    def test_correct_string_date(self):
        """Test if true is return when date is correct and entered as string"""
        self.assertTrue(is_correct_date('2011', '07', '12'))

    def test_incorrect_year(self):
        """We put a year < 1900"""
        self.assertFalse(is_correct_date('211', '07', '12'))

    def test_incorrect_year_int(self):
        """We put a year < 1900, passed as an int"""
        self.assertFalse(is_correct_date(211, 07, 12))

    def test_incorrect_month(self):
        """We put a year > 12"""
        self.assertFalse(is_correct_date('2011', '13', '12'))

    def test_negative_month(self):
        """We put a month < 0"""
        self.assertFalse(is_correct_date('2011', '-1', '12'))

    def test_far_incorrect_day(self):
        """Test when day > 31""" 
        self.assertFalse(is_correct_date('2011', '07', '42'))

    def test_incorrect_feb_29(self):
        """Test with an inccorect february 29th"""
        self.assertFalse(is_correct_date('2011', '02', '29'))

    def test_with_non_digit_strings(self):
        """Test what happens when we send garbage as params"""
        self.assertFalse(is_correct_date('tic', 'tac', 'toe'))
        

if __name__ == '__main__':
    unittest.main()
