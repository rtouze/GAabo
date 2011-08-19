#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This module tests the exporters classes for subscriber list"""

import unittest
import os
import sqlite3
import codecs
import datetime

import gaabo_conf
from subscriber import Subscriber
import subscriber_exporter

TEST_FILE = 'export_test.csv'

class AbstractExportTest(unittest.TestCase):
    """Abstract Class that can be used for all Export tests"""
    def setUp(self):
        """Common setup method that reset the test DB"""
        reset_test_db()
        gaabo_conf.db_name = 'test.db'
        self.exporter = None

    def tearDown(self):
        """Delete generated file"""
        os.remove(TEST_FILE)

    def export_and_get_first_line(self):
        """Perform the export with provided exporter and extract file first
        line"""
        self.exporter.do_export()
        return get_first_line()

class RoutageExportTest(AbstractExportTest):
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
        """Call common setup and create the RoutageExporter"""
        AbstractExportTest.setUp(self)
        self.exporter = subscriber_exporter.RoutageExporter(TEST_FILE)

    def test_first_line(self):
        """Test if the first line of generated file is well written"""

        subs = Subscriber()
        subs.lastname = 'Debelle'
        subs.firstname = 'Anne'
        subs.address = 'rue dupre 63'
        subs.address_addition = 'Bruxelles 1090'
        subs.city = 'belgique'
        subs.issues_to_receive = 1
        subs.save()

        line = self.export_and_get_first_line()

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
        """Test if a subscriber that has no issue left will not receive a free
        number :)"""
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
        """Test if exported file contains toto but not tata"""
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
        """Test the function to export subscriber list to send special issue"""
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
        """test if the fields in the output file does not exceed character limits"""
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
        line = self.export_and_get_first_line()

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
        line = self.export_and_get_first_line()
        splitted_line = line.split('\t')
        self.assertEqual(splitted_line[8], '01300')

    def test_noexception_with_emtpy_string_postcode(self):
        """Test that former empty postcode leads to no export error exception"""
        subscriber = Subscriber()
        subscriber.lastname = 'toto'
        subscriber.post_code = ''
        subscriber.save()
        line = self.export_and_get_first_line()
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
        line = self.export_and_get_first_line()
        splitted = line.split('\t')
        self.assertEqual('CHEZ LULU', splitted[5])
        self.assertEqual('14 RUE LALALA', splitted[6])

class CsvExporterTest(AbstractExportTest):
    """Tests class for the CsvExporter from subscriber_exporter module"""

    def setUp(self):
        AbstractExportTest.setUp(self)
        self.exporter = subscriber_exporter.CsvExporter(TEST_FILE)
        
    def test_header(self):
        """Test the heading line of the file"""
        actual = self.export_and_get_first_line()
        expected_head = (
                u'nom;société;ville/pays;' +
                u'numeros à recevoir;HS à recevoir;' + 
                'prix abonnement;prix cottisation;' + 
                'date abonnement\r\n'
                )
        self.assertEqual(expected_head, actual)

    def test_basic_line(self):
        """Test that firstname / lastname field is correct"""
        self.save_basic_subscriber() 
        self.exporter.do_export()
        actual_line = get_second_line()
        expected_line = 'John Doe;Apave;Rouen;5;6;20.0;30.0;12/07/2011\r\n'
        self.assertEquals(expected_line, actual_line)

    def test_accent_line(self):
        """Test that we can retrieve non ascii information"""
        self.save_accent_subscriber()
        self.exporter.do_export()
        actual_line = get_second_line().split(';')[0]
        expected_line_begin = u'Bébé Yé'
        self.assertEquals(expected_line_begin, actual_line)

    def test_date_error(self):
        """Test the behaviour of the code when we have an error in date"""
        self.save_wrong_date_subscriber()
        self.exporter.do_export()
        actual_line = get_second_line()
        expected_line = u'John Doe;;;6;0;0.0;0.0;12/07/0211\r\n'
        self.assertEquals(expected_line, actual_line)

    def save_wrong_date_subscriber(self):
        sub = Subscriber()
        sub.lastname = 'Doe'
        sub.firstname = 'John'
        sub.subscription_date = datetime.date(211, 07, 12)
        sub.save()

    def save_basic_subscriber(self):
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

    def save_accent_subscriber(self):
        sub = Subscriber()
        sub.lastname = u'Yé'
        sub.firstname = u'Bébé'
        sub.save()

class ResubscribingTest(AbstractExportTest):
    """This class tests the generation of the CSV file for re-subscribing
    mailing campaign.

    Bellow is the description of what we expect for field in the file:
    - firstname lastname and / or company
    - address1 (names addition)
    - address2 (address)
    - address2 (address addition)
    - post code
    - city or country

    Fields are separated by semi colon, which is a delimiter known by all
    spresdsheet editors that I know"""

    def setUp(self):
        """Setup class. Initialize in memory db"""
        AbstractExportTest.setUp(self)
        self.exporter = subscriber_exporter.ReSubscribeExporter(TEST_FILE)
        self.regular_subscriber_line = \
                'PRENOM NOM;NAMEADDITION;ADRESSE;ADDITION;12345;VILLE\n'
        self.company_subscriber_line = \
                'CAPGEMINI, POUR PRENOM NOM;' + \
                'NAMEADDITION;ADRESSE;ADDITION;12345;VILLE\n'

    def test_regular_subscriber(self):
        """Tests if the coordinates of a regular subscriber are OK in the
        file"""
        self.init_regular_subscriber()
        self.exporter.do_export()
        actual_line = get_second_line()

        expected_line = self.regular_subscriber_line 

        self.assertEqual(expected_line, actual_line)

    def init_regular_subscriber(self):
        """Initialize a regular subscriber, in France, without company with no
        issue to receive."""
        sub = self.set_regular_subscriber() 
        sub.issues_to_receive = 0
        sub.save()

    def set_regular_subscriber(self):
        sub = Subscriber()
        sub.lastname = 'Nom'
        sub.firstname = 'Prenom'
        sub.name_addition = 'NameAddition'
        sub.address = 'Adresse'
        sub.address_addition = 'Addition'
        sub.post_code = '12345'
        sub.city = 'Ville'
        return sub

    def test_header_line(self):
        actual_line = self.export_and_get_first_line()

        expected_line = u'Destinataire;Adresse1;Adresse2;' + \
                u'Adresse3;Code Postal;Ville / Pays\n'

        self.assertEqual(expected_line, actual_line)

    def test_non_ending_subscriber(self):
        self.init_regular_subscriber_with_issues_to_receive()
        self.exporter.do_export()

        actual_line = get_second_line()
        expected_line = u''

        self.assertEqual(expected_line, actual_line)

    def init_regular_subscriber_with_issues_to_receive(self):
        """Initialize a regular subscriber, in France, without company with one
        issue to receive."""
        sub = self.set_regular_subscriber() 
        sub.issues_to_receive = 1
        sub.save()

    def test_company_subscriber(self):
        self.init_company_subscriber()
        self.exporter.do_export()

        actual_line = get_second_line()
        expected_line = self.company_subscriber_line

        self.assertEqual(expected_line, actual_line)

    def init_company_subscriber(self):
        """Initialize a regular subscriber with a company name"""
        sub = self.set_regular_subscriber() 
        sub.issues_to_receive = 0
        sub.company = 'Capgemini'
        sub.save()


    def test_company_without_lastname(self):
        self.init_company_subscriber_without_name()
        self.exporter.do_export()

        actual_line = get_second_line()
        expected_line = self.get_company_without_name_subscriber_line()

        self.assertEqual(expected_line, actual_line)

    def init_company_subscriber_without_name(self):
        """Initialize a subscriber without name info but with company info."""
        sub = Subscriber()
        sub.company = 'Google'
        sub.address = 'Address'
        sub.city = 'USA'
        sub.issues_to_receive = 0
        sub.save()

    def get_company_without_name_subscriber_line(self):
        return u'GOOGLE;;ADDRESS;;;USA\n'

class EmailExporterTest(AbstractExportTest):
    """This class tests the fonctionnality to unload the email list of
    subscribers with ended subscription. The extracted emails are stored in a
    file separated by commas in order to put them in the Bcc field of an
    email"""

    def setUp(self):
        AbstractExportTest.setUp(self)
        self.exporter = subscriber_exporter.EmailExporter(TEST_FILE)

    def test_one_email(self):
        """Test retrieval of one subscriber's email"""
        subscriber = Subscriber()
        subscriber.issues_to_receive = 0
        subscriber.email_address = 'toto@example.com'
        subscriber.save()
        line = self.export_and_get_first_line()

        self.assertEqual('toto@example.com', line.strip())

    def test_two_email(self):
        """Tests when we have two emails in generated file"""
        subscriber = Subscriber()
        subscriber.email_address = 'toto@example.com'
        subscriber.issues_to_receive = 0
        subscriber.save()
        subscriber = Subscriber()
        subscriber.email_address = 'tata@example.com'
        subscriber.issues_to_receive = 0
        subscriber.save()
        line = self.export_and_get_first_line()

        self.assertEqual('toto@example.com,tata@example.com\n', line)

    def test_remaining_issues_subscriber(self):
        """Tests when the subscriber has remaining issues"""
        subs = Subscriber()
        subs.issues_to_receive = 1
        subs.email_address = 'tata@example.com'
        subs.save()
        line = self.export_and_get_first_line()
        self.assertEqual('', line)

    def test_remaining_special_issues_subscriber(self):
        """Tests when the subscriber has remaining special issues"""
        subs = Subscriber()
        subs.issues_to_receive = 0
        subs.hors_serie1 = 1
        subs.email_address = 'tata@example.com'
        subs.save()
        line = self.export_and_get_first_line()
        self.assertEqual('', line)

    def test_subscriber_with_regular_and_special(self):
        """Test when subscriber has both remaining regular and special issues"""
        subs = Subscriber()
        subs.issues_to_receive = 1
        subs.hors_serie1 = 1
        subs.email_address = 'tata@example.com'
        subs.save()
        line = self.export_and_get_first_line()
        self.assertEqual('', line)

    def test_email_in_lowercase(self):
        """Tests that in generated file, the emails are in lower case"""
        subscriber = Subscriber()
        subscriber.issues_to_receive = 0
        subscriber.email_address = 'tOTo@exAmpLE.COm'
        subscriber.save()
        line = self.export_and_get_first_line()
        self.assertEqual('toto@example.com', line.strip())

    def test_empty_email(self):
        """Tests what appens when a subscriber has no email"""
        subscriber = Subscriber()
        subscriber.email_address = 'toto@example.com'
        subscriber.issues_to_receive = 0
        subscriber.save()
        subscriber = Subscriber()
        subscriber.email_address = ''
        subscriber.issues_to_receive = 0
        subscriber.save()
        line = self.export_and_get_first_line()

        self.assertEqual('toto@example.com\n', line)

    
def reset_test_db():
    conn = sqlite3.Connection('../databases/test.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM subscribers')
    conn.commit()
    conn.close()

def get_second_line():
    """Get the first data line, which should be the second line of the
    file"""
    test_file = open_test_file()
    test_file.readline()
    line = test_file.readline()
    test_file.close()
    return line

def open_test_file():
    return codecs.open(TEST_FILE, 'r', 'utf-8')

def get_first_line():
    """Get the first line of an exporter file, which can contain a header or
    regular data"""
    test_file = open_test_file()
    line = test_file.readline()
    test_file.close()
    return line

if __name__ == '__main__':
    unittest.main()
