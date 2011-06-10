#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module tests the generation of the CSV file for re-subscribing mailing
campaign.

Bellow is the description of what we expect for field in the file:
- firstname lastname and / or company
- address
- address addition (useful for subscribers abroad)
- post code
- city or country

Fields are separated by semi colon, which is a delimiter known by all
spresdsheet editors that I know"""

import unittest
import sqlite3
import os
import codecs

import gaabo_conf
from subscriber_exporter import ReSubscribeExporter
from subscriber import Subscriber
from gaabo_exploit_db import SqliteDbOperator

TEST_FILE = 'export_test.csv'

class ResubscribingTest(unittest.TestCase):
    """testing class"""

    def setUp(self):
        """Setup class. Initialize in memory db"""
        reset_test_db()
        gaabo_conf.db_name = 'test.db'

    def test_regular_subscriber(self):
        """Tests if the coordinates of a regular subscriber are OK in the
        file"""
        
        init_regular_subscriber()
        export_data_in_test_file()

        actual_line = get_first_data_line()
        expected_line = get_regular_subscriber_line() 

        self.assertEqual(expected_line, actual_line)

    def test_header_line(self):
        export_data_in_test_file()

        actual_line = get_header_line()
        expected_line = u'Destinataire;Adresse;Complement Adresse;' + \
                u'Code Postal;Ville / Pays\n'

        self.assertEqual(expected_line, actual_line)

    def test_non_ending_subscriber(self):
        init_regular_subscriber_with_issues_to_receive()
        export_data_in_test_file()

        actual_line = get_first_data_line()
        expected_line = u''

        self.assertEqual(expected_line, actual_line)

    def test_company_subscriber(self):
        init_company_subscriber()
        export_data_in_test_file()

        actual_line = get_first_data_line()
        expected_line = get_company_subscriber_line()

        self.assertEqual(expected_line, actual_line)

    def test_company_without_lastname(self):
        init_company_subscriber_without_name()
        export_data_in_test_file()

        actual_line = get_first_data_line()
        expected_line = get_company_without_name_subscriber_line()

        self.assertEqual(expected_line, actual_line)

    def tearDown(self):
        """Close the testfile"""
        os.remove(TEST_FILE)
    
def reset_test_db():
    conn = sqlite3.Connection('../databases/test.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subscribers')
    conn.commit()
    conn.close()

def init_regular_subscriber():
    """Initialize a regular subscriber, in France, without company with no
    issue to receive."""
    sub = get_regular_subscriber() 
    sub.issues_to_receive = 0
    sub.save()

def get_regular_subscriber():
    sub = Subscriber()
    sub.lastname = 'Nom'
    sub.firstname = 'Prenom'
    sub.address = 'Adresse'
    sub.address_addition = 'Addition'
    sub.post_code = '12345'
    sub.city = 'Ville'
    return sub

def get_regular_subscriber_line():
    return u'PRENOM NOM;ADRESSE;ADDITION;12345;VILLE\n'

def init_regular_subscriber_with_issues_to_receive():
    """Initialize a regular subscriber, in France, without company with one
    issue to receive."""
    sub = get_regular_subscriber() 
    sub.issues_to_receive = 1
    sub.save()

def init_company_subscriber():
    """Initialize a regular subscriber with a company name"""
    sub = get_regular_subscriber() 
    sub.issues_to_receive = 0
    sub.company = 'Capgemini'
    sub.save()

def get_company_subscriber_line():
    return u'CAPGEMINI, POUR PRENOM NOM;ADRESSE;ADDITION;12345;VILLE\n'

def init_company_subscriber_without_name():
    """Initialize a subscriber without name info but with company info."""
    sub = Subscriber()
    sub.company = 'Google'
    sub.address = 'Address'
    sub.city = 'USA'
    sub.issues_to_receive = 0
    sub.save()

def get_company_without_name_subscriber_line():
    return u'GOOGLE;ADDRESS;;;USA\n'


def export_data_in_test_file():
    exporter = ReSubscribeExporter(TEST_FILE)
    exporter.do_export()

def get_first_data_line():
    """Get the first data line, which should be the second line of the
    file"""
    test_file = codecs.open(TEST_FILE, 'r', 'utf-8')
    test_file.readline()
    line = test_file.readline()
    test_file.close()
    return line

def get_header_line():
    test_file = codecs.open(TEST_FILE, 'r', 'utf-8')
    line = test_file.readline()
    test_file.close()
    return line

if __name__ == '__main__':
    unittest.main()
