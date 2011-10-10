#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test module for gaabo_controler"""

__author__ = 'romain.touze@gmail.com'

import unittest
from datetime import date

from gaabo_controler import SubscriberAdapter
import gaabo_conf
from subscriber import Subscriber
from subscriber import Address
import sqlite3

class SubscriberAdapterAbstractTest(unittest.TestCase):
    def setUp(self):
        """Initialize the object and database"""
        gaabo_conf.db_name = 'test.db'
        self.conn = sqlite3.Connection('../databases/test.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('DELETE FROM subscribers')
        self.conn.commit()

class SubscriberAdapterTest(SubscriberAdapterAbstractTest):

    def test_simple_subscriber_save_retrieve(self):
        """Test subscriber save with few fields"""
        sub = {
                'lastname': 'toto',
                'firstname': 'tata',
                'email_address': 'toto@truc.com'
                }

        actual = self._save(sub)
        self.assertEquals('toto', actual['lastname'])
        self.assertTrue('subscriber_id' in actual.keys())
        
        retrieved_sub = self._retrieve_one_from_lastname('toto')
        self.assertEquals(retrieved_sub.firstname, 'tata')
        self.assertEquals(retrieved_sub.email_address, 'toto@truc.com')
        self.assertEquals(retrieved_sub.identifier, actual['subscriber_id'])

    def _save(self, sub):
        """Save the subscriber"""
        adapter = SubscriberAdapter(sub)
        actual = adapter.save_subscriber()
        return actual

    def _retrieve_one_from_lastname(self, lastname):
        """Retrieve the first sub in db having provided lastname"""
        subs_list = Subscriber.get_subscribers_from_lastname(lastname)
        return subs_list[0]

    def test_unicode_subs(self):
        sub = {
                'lastname': 'toto',
                'firstname': u'tété'
                }
        retrieved_sub = self._save_and_retrieve_from_lastname(sub, 'toto')
        self.assertEquals(u'tété', retrieved_sub.firstname)

    def test_subscriber_with_id(self):
        db_sub = Subscriber()
        db_sub.lastname = 'toto'
        db_sub.firstname = 'tata'
        db_sub.save()
        ident = db_sub.identifier
        sub = {
                'subscriber_id': ident,
                'lastname': 'toto',
                'firstname': 'titi'
                }
        actual = self._save(sub)
        self.assertEquals(ident, actual['subscriber_id'])
        
        retrieved_sub = self._retrieve_one_from_lastname('toto')
        self.assertEquals(ident, retrieved_sub.identifier)

    def test_subscriber_with_address_retrieve(self):
        """Test saving and retrieving a subscriber with address"""
        sub = {
                'lastname': 'toto',
                'firstname': 'tata',
                'email_address': 'toto@truc.com',
                'company': 'google',
                'name_addition': 'appt 42',
                'address': '10 rue boubou',
                'address_addition': 'foobar',
                'post_code': '38000',
                'city': 'Grenoble',
                }
        retrieved_sub = self._save_and_retrieve_from_lastname(sub, 'toto')
        retrieved_address = retrieved_sub.address

        self.assertEquals(sub['company'], retrieved_sub.company)
        self.assertEquals(sub['name_addition'], retrieved_sub.name_addition)
        self.assertEquals(sub['address'], retrieved_address.address1)
        self.assertEquals(sub['address_addition'], retrieved_address.address2)
        self.assertEquals(sub['post_code'], str(retrieved_address.post_code))
        self.assertEquals(sub['city'], retrieved_address.city)

    def _save_and_retrieve_from_lastname(self, sub, lastname):
        """Call _save, then _retrieve_one_from_lastname with provided info"""
        self._save(sub)
        return self._retrieve_one_from_lastname(lastname)

    def test_subscriber_without_identification(self):
        """Test a subscriber without lastname, firstname nor email"""
        sub = {
                'company': 'google',
                'name_addition': 'appt 42',
                }
        self._save(sub)
        subs_list = Subscriber.get_subscribers_from_company('google')
        retrieved_sub = subs_list[0]
        retrieved_address = retrieved_sub.address

        self.assertEquals(sub['company'], retrieved_sub.company)
        self.assertEquals(sub['name_addition'], retrieved_sub.name_addition)

    def test_subscriber_with_subscription_info(self):
        """Test a subscriber having a subscription"""
        sub = {
                'lastname': 'toto',
                'subscriber_since_issue':'32',
                'subscription_date':'03/10/2011',
                'issues_to_receive':'5',
                'subs_beginning_issue':'31',
                'hors_serie1':'1'
                }
        retrieved = self._save_and_retrieve_from_lastname(sub, 'toto')
        self.assertEquals(
                sub['subscriber_since_issue'],
                str(retrieved.subscriber_since_issue)
                )
        self.assertEquals(
                sub['issues_to_receive'],
                str(retrieved.issues_to_receive)
                )
        self.assertEquals(
                sub['subs_beginning_issue'],
                str(retrieved.subs_beginning_issue)
                )
        self.assertEquals(
                sub['hors_serie1'],
                str(retrieved.hors_serie1)
                )

    def test_empty_subscription_info(self):
        sub = {
                'lastname': 'toto',
                'subscriber_since_issue':'',
                'subscription_date':'',
                'issues_to_receive':'',
                'subs_beginning_issue':'',
                'hors_serie1':''
                }
        retrieved = self._save_and_retrieve_from_lastname(sub, 'toto')
        self.assertEquals(0, retrieved.subscriber_since_issue)
        self.assertEquals(
                date.today(),
                retrieved.subscription_date
                )
        


    def test_pricing_info(self):
        """Tests float info abour subscription pricing"""
        sub = {
                'lastname': 'toto',
                'subscription_price':'37,2',
                'membership_price':'50,1',
                }
        retrieved = self._save_and_retrieve_from_lastname(sub, 'toto')
        self.assertEquals(
                sub['subscription_price'],
                str(retrieved.subscription_price).replace('.', ',')
                )
        self.assertEquals(
                sub['membership_price'],
                str(retrieved.membership_price).replace('.', ',')
                )

    def test_other_misc_info(self):
        """Tests comment and ordering type fields"""
        sub = {
                'lastname': 'toto',
                'ordering_type':'pp',
                'comment':'blah blah'
                }
        retrieved = self._save_and_retrieve_from_lastname(sub, 'toto')
        self.assertEquals(
                sub['ordering_type'],
                str(retrieved.ordering_type)
                )
        self.assertEquals(
                sub['comment'],
                str(retrieved.comment)
                )

    def test_subscription_date(self):
        """Test behaviour of subscription date"""
        sub = {
                'lastname': 'toto',
                'subscriber_since_issue':'32',
                'subscription_date':'03/10/2011'
                }
        retrieved = self._save_and_retrieve_from_lastname(sub, 'toto')
        self.assertEquals(
                sub['subscription_date'],
                retrieved.subscription_date.strftime('%d/%m/%Y')
                )


class SubscriberRetrievalTest(SubscriberAdapterAbstractTest):
    """Tests subscriber retrieval and translation using the adapter"""

    def test_get_subs_by_lastname(self):
        """Test subscriber by lastname retrieval using the adapter"""
        sub = Subscriber()
        sub.lastname = 'toto'
        sub.firstname = 'tata'
        sub.email_address = 'toto@machin.com'
        sub.name_addition = 'foobar'
        sub.save()
        
        dict_list = SubscriberAdapter.get_subscribers_from_lastname('toto')
        new_sub = dict_list[0]
        self.assertEquals('toto', new_sub['lastname'])
        self.assertEquals('tata', new_sub['firstname'])
        self.assertEquals('toto@machin.com', new_sub['email_address'])
        self.assertEquals('foobar', new_sub['name_addition'])
        self.assertEquals(sub.identifier, new_sub['subscriber_id'])

    def test_get_subs_address_by_lastname(self):
        """Tests address fields on dict retrieved by the adapter"""
        sub = Subscriber()
        sub.lastname = 'toto'
        address = Address()
        address.address1 = '42 rue truc'
        address.address2 = 'bat B'
        address.post_code = 38100
        address.city = 'Paris'
        sub.address = address
        sub.save()

        dict_list = SubscriberAdapter.get_subscribers_from_lastname('toto')
        new_sub = dict_list[0]
        self.assertEquals('42 rue truc', new_sub['address'])
        self.assertEquals('bat B', new_sub['address_addition'])
        self.assertEquals('38100', new_sub['post_code'])
        self.assertEquals('Paris', new_sub['city'])

    def test_subscription_info_by_lastname(self):
        """Test subscription info fields retrieved by the adapter"""
        sub = Subscriber()
        sub.lastname = 'toto'
        sub.subscription_date = date(2011, 10, 10)
        sub.issues_to_receive = 5
        sub.subs_beginning_issue = 32
        sub.subscription_price = 31.50
        sub.membership_price = 50.25
        sub.hors_serie1 = 1
        sub.ordering_type = 'pp'
        sub.comment = 'blahblah'
        sub.save()

        dict_list = SubscriberAdapter.get_subscribers_from_lastname('toto')
        new_sub = dict_list[0]
        self.assertEquals('10/10/2011', new_sub['subscription_date'])
        self.assertEquals('5', new_sub['issues_to_receive'])
        self.assertEquals('32', new_sub['subs_beginning_issue'])
        self.assertEquals('31,50', new_sub['subscription_price'])
        self.assertEquals('50,25', new_sub['membership_price'])
        self.assertEquals('1', new_sub['hors_serie1'])
        self.assertEquals('pp', new_sub['ordering_type'])
        self.assertEquals('blahblah', new_sub['comment'])

    def test_get_subs_by_company(self):
        """Test subscriber by company retrieval using the adapter"""
        sub = Subscriber()
        sub.lastname = 'toto'
        sub.firstname = 'tata'
        sub.company = 'Machin.corp'
        sub.email_address = 'toto@machin.com'
        sub.name_addition = 'foobar'
        sub.save()
        
        dict_list = SubscriberAdapter.get_subscribers_from_company('Machin.corp')
        new_sub = dict_list[0]
        self.assertEquals('toto', new_sub['lastname'])
        self.assertEquals('tata', new_sub['firstname'])
        self.assertEquals('toto@machin.com', new_sub['email_address'])
        self.assertEquals('foobar', new_sub['name_addition'])
        self.assertEquals('Machin.corp', new_sub['company'])
        self.assertEquals(sub.identifier, new_sub['subscriber_id'])

    def test_get_subs_by_email(self):
        """Test subscriber by email retrieval using the adapter"""
        sub = Subscriber()
        sub.lastname = 'toto'
        sub.firstname = 'tata'
        sub.company = 'Machin.corp'
        sub.email_address = 'toto@machin.com'
        sub.name_addition = 'foobar'
        sub.save()
        
        dict_list = SubscriberAdapter.get_subscribers_from_email('toto@machin.com')
        new_sub = dict_list[0]
        self.assertEquals('toto', new_sub['lastname'])
        self.assertEquals('tata', new_sub['firstname'])
        self.assertEquals('toto@machin.com', new_sub['email_address'])
        self.assertEquals('foobar', new_sub['name_addition'])
        self.assertEquals('Machin.corp', new_sub['company'])
        self.assertEquals(sub.identifier, new_sub['subscriber_id'])

if __name__ == '__main__':
    unittest.main()
