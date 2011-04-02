#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Test module for the subscriber_importer module.'''
import unittest
import sqlite3
import os
import subscriber_importer
from subscriber import Subscriber
import datetime
import gaabo_conf
from gaabo_exploit_db import SqliteDbOperator

class TestSubscriberImporter(unittest.TestCase):
    '''unittest class that performs the tests'''

    def test_emilie_feugere(self):
        '''Tests if the information of subscriber Emilie Feugere are well imported'''
        sub = Subscriber.get_subscribers_from_lastname('Feugere')[0]
        self.assertEquals(sub.lastname, 'Feugere')
        self.assertEquals(sub.firstname, 'Emilie')
        self.assertEquals(
                sub.subscription_date,
                unicode(datetime.date(2009, 11, 8))
                )
        self.assertEquals(sub.issues_to_receive, 0)
        self.assertEquals(sub.subs_beginning_issue, 21)
        self.assertEquals(sub.ordering_type, 'ch')
        self.assertEquals(sub.address, '67 rue de la raffiniere')
        self.assertEquals(sub.post_code, 85350)
        self.assertEquals(sub.city, """Ile d'Yeu""")
        self.assertEquals(sub.subscription_price, 27)
        self.assertEquals(sub.membership_price, 13)
        self.assertEquals(sub.email_address, 'xavier.gicqueau@club-internet.fr')
        self.assertEquals(sub.subscriber_since_issue, 15)
        self.assertEquals(sub.sticker_sent, 1)
        self.assertEquals(sub.member, 1)

    def test_bibli_lyon(self):
        '''Tests if the information of company subscriber Bibliotheque de la
        ville de Lyon are well imported'''
        company = 'Bibliotheque de la ville de lyon'
        sub = Subscriber.get_subscribers_from_company(company)[0]
        self.assertEquals(sub.company, company)
        self.assertEquals(sub.name_addition, 'service des periodiques')

    def test_jean_fabala(self):
        '''Tests if the information for Mediateque Jean Fabala are well
        imported'''
        company = 'Mediatheque Jean Falala'
        sub = Subscriber.get_subscribers_from_company(company)[0]
        self.assertEquals(sub.bank, 'ebsco')

    def test_anne_debelle(self):
        '''Tests if the information for Anne Debelle are right'''
        name = 'Anne Debelle'
        sub = Subscriber.get_subscribers_from_lastname(name)[0]
        self.assertEquals(sub.address_addition, 'Bruxelles 1090')
        self.assertEquals(sub.hors_serie1, 7)

    def test_lopez(self):
        '''Test to see if accent chars are imported'''
        name = 'lopez'
        sub = Subscriber.get_subscribers_from_lastname(name)[0]
        self.assertEquals(sub.address, u'31 allée des loges')

if __name__ == '__main__':
    gaabo_conf.db_name = 'test.db'
    db_ex = SqliteDbOperator()
    db_ex.remove_db()
    import_file_name = 'data/import_subscriber_test.txt'
    importer = subscriber_importer.SubscriberImporter(import_file_name)
    importer.do_truncate_import()
    unittest.main()
