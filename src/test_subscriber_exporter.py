#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''This module tests the exporters classes for subscriber list'''

import gaabo_conf
import unittest

import os
import sqlite3
import subscriber_importer
import codecs
import datetime

from subscriber import Subscriber
from subscriber_exporter import *

TEST_FILE = 'export_test.csv'

class RoutageExportTest(unittest.TestCase):
    """Test class for RoutageExporter object
    Rotage format:
        1 - N° de client      20 chars max
        2 - Civilité (M, MME) 12 chars max
        3 - Nom de client     32 chars max
        4 - Prénom de client  20 chars max
        5 - Nom de société    32 chars max
        6 - Adresse 1         32 chars max
        7 - Adresse 2         32 chars max
        8 - Adresse 3             32 chars max
        9 - Code postal            5 chars max
        10 - Ville                26 chars max
        11 - Nombre d’exemplaires  8 chars max
        12 - Mode d’envoi          3 chars max
        13 - Information libre 1  32 chars max
        14 - Information libre 2  32 chars max
        15 - Information libre 3  32 chars max
        16 - Information libre 4  32 chars max
       """ 
    def setUp(self):
        '''Define the file name and reset the DB'''
        reset_test_db()
        gaabo_conf.db_name = 'test.db'
        self.exporter = RoutageExporter(TEST_FILE)

    def test_first_line(self):
        '''Test if the first line of generated file is well written'''

        subs = Subscriber()
        subs.lastname = 'Debelle'
        subs.firstname = 'Anne'
        subs.address = 'rue dupre 63'
        subs.address_addition = 'Bruxelles 1090'
        subs.city = 'belgique'
        subs.issues_to_receive = 1
        subs.save()

        self.exporter.do_export()

        line = get_first_line()
        self.assertTrue(line is not None)

        splitted_line = line.split('\t')
        self.assertEquals(splitted_line[2], u'DEBELLE')
        self.assertEquals(splitted_line[3], u'ANNE')
        self.assertEquals(splitted_line[4], u'')
        self.assertEquals(splitted_line[5], u'')
        self.assertEquals(splitted_line[6], u'RUE DUPRE 63')
        self.assertEquals(splitted_line[7], u'BRUXELLES 1090')
        self.assertEquals(splitted_line[8], u'')
        self.assertEquals(splitted_line[9], u'BELGIQUE')
        self.assertEquals(splitted_line[10], u'')
        self.assertEquals(splitted_line[11], u'')
        self.assertEquals(splitted_line[12], u'')
        self.assertEquals(splitted_line[13], u'')
        self.assertEquals(splitted_line[14], u'')
        self.assertEquals(splitted_line[15], u'\n')

    def test_subscriber_without_remaining_issue(self):
        '''Test if a subscriber that has no issue left will not receive a free
        number :)'''
        subscriber = Subscriber()
        subscriber.lastname = 'toto'
        subscriber.issues_to_receive = 1
        subscriber.save()
        subscriber = Subscriber()
        subscriber.lastname = 'tata'
        subscriber.issues_to_receive = 0
        subscriber.save()
        self.exporter.do_export()

        self.__test_presence_toto_tata()

    def __test_presence_toto_tata(self):
        '''Test if exported file contains toto but not tata'''
        file_pointer = open(TEST_FILE, 'r')
        has_toto = 0
        has_tata = 0

        for line in file_pointer:
            if line.find('TOTO') != -1:
                has_toto = 1
            if line.find('TATA') != -1:
                has_tata = 1
        file_pointer.close()

        self.assertEquals(has_toto, 1, 'toto not found')
        self.assertEquals(has_tata, 0, 'tata found')

    def test_export_for_special_issues(self):
        '''Test the function to export subscriber list to send special issue'''
        subscriber = Subscriber()
        subscriber.lastname = 'toto'
        subscriber.hors_serie1 = 1
        subscriber.hors_serie2 = 0
        subscriber.hors_serie3 = 0
        subscriber.save()
        subscriber = Subscriber()
        subscriber.lastname = 'tata'
        subscriber.hors_serie1 = 0
        subscriber.hors_serie2 = 1
        subscriber.hors_serie3 = 0
        subscriber.save()

        self.exporter.do_export_special_issue()

        self.__test_presence_toto_tata()

    def test_field_length(self):
        '''test if the fields in the output file does not exceed character limits'''
        big_string = ''.join(['b' for i in xrange(1, 40)])
        subscriber = Subscriber()
        subscriber.lastname = big_string
        subscriber.firstname = big_string
        subscriber.company = big_string
        subscriber.address = big_string
        subscriber.address_addition = big_string
        subscriber.post_code = 123456 
        subscriber.issues_to_receive = 10
        subscriber.city = big_string
        subscriber.save()
        self.exporter.do_export()
        line = get_first_line()

        splitted_line = line.split('\t')
        self.assertTrue(len(splitted_line[0]) <= 20)
        self.assertTrue(len(splitted_line[1]) <= 12)
        self.assertTrue(len(splitted_line[2]) <= 32)
        self.assertTrue(len(splitted_line[3]) <= 20)
        self.assertTrue(len(splitted_line[4]) <= 32)
        self.assertTrue(len(splitted_line[5]) <= 32)
        self.assertTrue(len(splitted_line[6]) <= 32)
        self.assertTrue(len(splitted_line[7]) <= 32)
        self.assertTrue(len(splitted_line[8]) <= 5)
        self.assertTrue(len(splitted_line[9]) <= 26)
        self.assertTrue(len(splitted_line[10]) <= 8)
        self.assertTrue(len(splitted_line[11]) <= 3)
        self.assertTrue(len(splitted_line[12]) <= 32)
        self.assertTrue(len(splitted_line[13]) <= 32)
        self.assertTrue(len(splitted_line[14]) <= 32)
        self.assertTrue(len(splitted_line[15]) <= 32)

    def test_non_ascii_char(self):
        subscriber = Subscriber()
        subscriber.lastname = u'Toto°°'
        subscriber.issues_to_receive = 1
        subscriber.save()
        line = get_first_line()
        self.assertTrue(line is not None)

    def test_5_digit_post_code(self):
        """Checks that the exported post_code is always written with 5 digits,
        even if the first one is 0."""
        subscriber = Subscriber()
        subscriber.post_code = 1300
        subscriber.save()
        self.exporter.do_export()
        line = get_first_line()
        splitted_line = line.split('\t')
        self.assertEqual(splitted_line[8], '01300')

    def test_noexception_with_emtpy_string_postcode(self):
        """Test that former empty postcode leads to no export error exception"""
        subscriber = Subscriber()
        subscriber.lastname = 'toto'
        subscriber.post_code = ''
        subscriber.save()
        self.exporter.do_export()
        line = get_first_line()
        self.assertEqual(line.split('\t')[8], '')

    def test_handle_name_addition(self):
        """Tests that if we have a name_addition, it goes in the first address
        field"""
        subscriber = Subscriber()
        subscriber.lastname = 'Dupond'
        subscriber.firstname = 'Toto'
        subscriber.name_addition = 'Chez lulu'
        subscriber.address = '14 Rue lalala'
        subscriber.save()
        self.exporter.do_export()
        line = get_first_line()
        splitted = line.split('\t')
        self.assertEqual('CHEZ LULU', splitted[5])
        self.assertEqual('14 RUE LALALA', splitted[6])

    def tearDown(self):
        '''Delete generated file'''
        os.remove(TEST_FILE)

class CsvExporterTest(unittest.TestCase):
    """Test class for the CsvExporter from subscriber_exporter module"""

    def setUp(self):
        self.conn = sqlite3.Connection('../databases/test.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('DELETE FROM subscribers')
        self.conn.commit()
        gaabo_conf.db_name = 'test.db'
        self.test_file = 'data/test_routage.csv'
        self.exporter = CsvExporter(self.test_file)
        

    def test_header(self):
        """Test the heading line of the file"""
        self.exporter.do_export()
        actual = self.read_first_line()
        expected_head = (
                u'nom;société;ville/pays;' +
                u'numeros à recevoir;HS à recevoir;' + 
                'prix abonnement;prix cottisation;' + 
                'date abonnement\r\n'
                )
        self.assertEqual(expected_head, actual)

    def read_first_line(self):
        file_descriptor = self.open_test_file()
        line = file_descriptor.readline()
        file_descriptor.close()
        return line

    def open_test_file(self):
        """Open test file using utf-8 encoding"""
        return codecs.open(self.test_file, 'r', 'utf-8')

    def test_basic_line(self):
        """Test that firstname / lastname field is correct"""
        save_basic_subscriber() 
        self.exporter.do_export()
        actual_line = self.read_second_line()
        expected_line = 'John Doe;Apave;Rouen;5;6;20.0;30.0;12/07/2011\r\n'
        self.assertEquals(expected_line, actual_line)

    def read_second_line(self):
        file_descriptor = self.open_test_file()
        file_descriptor.readline()
        line = file_descriptor.readline()
        file_descriptor.close()
        return line;

    def test_accent_line(self):
        """Test that we can retrieve non ascii information"""
        save_accent_subscriber()
        self.exporter.do_export()
        actual_line = self.read_second_line().split(';')[0]
        expected_line_begin = u'Bébé Yé'
        self.assertEquals(expected_line_begin, actual_line)

    def test_date_error(self):
        """Test the behaviour of the code when we have an error in date"""
        save_wrong_date_subscriber()
        self.exporter.do_export()
        actual_line = self.read_second_line()
        expected_line = u'John Doe;;;6;0;0.0;0.0;12/07/0211\r\n'
        self.assertEquals(expected_line, actual_line)

    def tearDown(self):
        os.remove(self.test_file)
        self.cursor.close()
        self.conn.close()


def save_basic_subscriber():
    sub = Subscriber()
    sub.lastname = 'Doe'
    sub.firstname = 'John'
    sub.company = 'Apave'
    sub.city = 'Rouen'
    sub.issues_to_receive = 5
    sub.hors_serie1 = 6
    sub.subscription_price = 20
    sub.membership_price = 30
    sub.subscription_date = datetime.date(2011, 07, 12)
    sub.save()

def save_accent_subscriber():
    sub = Subscriber()
    sub.lastname = u'Yé'
    sub.firstname = u'Bébé'
    sub.save()
    
def save_wrong_date_subscriber():
    sub = Subscriber()
    sub.lastname = 'Doe'
    sub.firstname = 'John'
    sub.subscription_date = datetime.date(211, 07, 12)
    sub.save()

class ResubscribingTest(unittest.TestCase):
    """This class tests the generation of the CSV file for re-subscribing
    mailing campaign.

    Bellow is the description of what we expect for field in the file:
    - firstname lastname and / or company
    - address
    - address addition (useful for subscribers abroad)
    - post code
    - city or country

    Fields are separated by semi colon, which is a delimiter known by all
    spresdsheet editors that I know"""

    def setUp(self):
        """Setup class. Initialize in memory db"""
        reset_test_db()
        gaabo_conf.db_name = 'test.db'

    def test_regular_subscriber(self):
        """Tests if the coordinates of a regular subscriber are OK in the
        file"""
        
        init_regular_subscriber()
        export_data_in_test_file()

        actual_line = get_second_line()
        expected_line = get_regular_subscriber_line() 

        self.assertEqual(expected_line, actual_line)

    def test_header_line(self):
        export_data_in_test_file()

        actual_line = get_first_line()
        expected_line = u'Destinataire;Adresse;Complement Adresse;' + \
                u'Code Postal;Ville / Pays\n'

        self.assertEqual(expected_line, actual_line)

    def test_non_ending_subscriber(self):
        init_regular_subscriber_with_issues_to_receive()
        export_data_in_test_file()

        actual_line = get_second_line()
        expected_line = u''

        self.assertEqual(expected_line, actual_line)

    def test_company_subscriber(self):
        init_company_subscriber()
        export_data_in_test_file()

        actual_line = get_second_line()
        expected_line = get_company_subscriber_line()

        self.assertEqual(expected_line, actual_line)

    def test_company_without_lastname(self):
        init_company_subscriber_without_name()
        export_data_in_test_file()

        actual_line = get_second_line()
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

def get_second_line():
    """Get the first data line, which should be the second line of the
    file"""
    test_file = codecs.open(TEST_FILE, 'r', 'utf-8')
    test_file.readline()
    line = test_file.readline()
    test_file.close()
    return line

def get_first_line():
    test_file = codecs.open(TEST_FILE, 'r', 'utf-8')
    line = test_file.readline()
    test_file.close()
    return line

if __name__ == '__main__':
    unittest.main()
