#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Test module for the subscriber_importer module.'''
import unittest
import sqlite3
import os
import datetime

import subscriber_importer
from subscriber import Subscriber
import gaabo_conf
from gaabo_exploit_db import SqliteDbOperator

imported_lines_number = 0

class TestSubscriberImporter(unittest.TestCase):
    """Tests for the regular subscriber importer class"""

    def test_emilie_feugere(self):
        '''Tests if the information of subscriber Emilie Feugere are well imported'''
        sub = Subscriber.get_subscribers_from_lastname('Feugere')[0]
        self.assertEqual(sub.lastname, 'Feugere')
        self.assertEqual(sub.firstname, 'Emilie')
        self.assertEqual(
                sub.subscription_date,
                datetime.date(2009, 11, 8)
                )
        self.assertEqual(sub.issues_to_receive, 0)
        self.assertEqual(sub.subs_beginning_issue, 21)
        self.assertEqual(sub.ordering_type, 'ch')
        self.assertEqual(sub.address, '67 rue de la raffiniere')
        self.assertEqual(sub.post_code, 85350)
        self.assertEqual(sub.city, """Ile d'Yeu""")
        self.assertEqual(sub.subscription_price, 27)
        self.assertEqual(sub.membership_price, 13)
        self.assertEqual(sub.email_address, 'xavier.gicqueau@club-internet.fr')
        self.assertEqual(sub.subscriber_since_issue, 15)
        self.assertEqual(sub.sticker_sent, 1)
        self.assertEqual(sub.member, 1)

    def test_bibli_lyon(self):
        '''Tests if the information of company subscriber Bibliotheque de la
        ville de Lyon are well imported'''
        company = 'Bibliotheque de la ville de lyon'
        sub = Subscriber.get_subscribers_from_company(company)[0]
        self.assertEqual(sub.company, company)
        self.assertEqual(sub.name_addition, 'service des periodiques')

    def test_jean_fabala(self):
        '''Tests if the information for Mediateque Jean Fabala are well
        imported'''
        company = 'Mediatheque Jean Falala'
        sub = Subscriber.get_subscribers_from_company(company)[0]
        self.assertEqual(sub.bank, 'ebsco')

    def test_anne_debelle(self):
        '''Tests if the information for Anne Debelle are right'''
        name = 'Anne Debelle'
        sub = Subscriber.get_subscribers_from_lastname(name)[0]
        self.assertEqual(sub.address_addition, 'Bruxelles 1090')
        self.assertEqual(sub.hors_serie1, 7)
        self.assertEqual(sub.membership_price, 15.5)

    def test_lopez(self):
        '''Test to see if accent chars are imported'''
        name = 'lopez'
        sub = Subscriber.get_subscribers_from_lastname(name)[0]
        self.assertEqual(sub.address, u'31 allée des loges')

    def test_imported_lines_counter(self):
        """Test if the number of read lines correspond to the number of lines
        in the files"""
        # We have 23 non empty rows - header row
        self.assertEqual(imported_lines_number, 22)

if __name__ == '__main__':
    gaabo_conf.db_name = 'test.db'
    db_ex = SqliteDbOperator()
    db_ex.remove_db()
    import_file_name = 'data/import_subscriber_test.txt'
    importer = subscriber_importer.SubscriberImporter(import_file_name)
    importer.do_truncate_import()
    imported_lines_number = importer.imported_lines_counter
    unittest.main()
