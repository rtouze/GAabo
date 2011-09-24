#!/usr/bin/env python
"""Test module for gaabo_controler"""

__author__ = 'romain.touze@gmail.com'

import unittest

import gaabo_controler
import gaabo_conf
from subscriber import Subscriber
import sqlite3


class SubscriberAdapterTest(unittest.TestCase):

    def setUp(self):
        '''Initialize the object and database'''
        gaabo_conf.db_name = 'test.db'
        self.conn = sqlite3.Connection('../databases/test.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('DELETE FROM subscribers')
        self.conn.commit()

    def test_simple_subscriber_save_retrieve(self):
        sub = {
                'lastname': 'toto',
                'firstname': 'tata',
                'email_address': 'toto@truc.com'
                }

        adapter = gaabo_controler.SubscriberAdapter(sub)
        actual = adapter.save_subscriber()
        self.assertEquals('toto', actual['lastname'])
        self.assertTrue('subscriber_id' in actual.keys())

        subs_list = Subscriber.get_subscribers_from_lastname('toto')
        retrieved_sub = subs_list[0]
        self.assertEquals(retrieved_sub.firstname, 'tata')
        self.assertEquals(retrieved_sub.email_address, 'toto@truc.com')
        self.assertEquals(retrieved_sub.identifier, actual['subscriber_id'])

if __name__ == '__main__':
    unittest.main()
