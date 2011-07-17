#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''This module tests the exporters classes for subscriber list'''

import gaabo_conf
import unittest
import subscriber_exporter
import os
import sqlite3
import subscriber_importer
import codecs
from subscriber import Subscriber

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
        self.conn = sqlite3.Connection('../databases/test.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('DELETE FROM subscribers')
        self.conn.commit()
        gaabo_conf.db_name = 'test.db'
        self.test_file = 'data/test_routage.txt'
        self.exporter = subscriber_exporter.RoutageExporter(self.test_file)

    def test_first_line(self):
        '''Test if the first line of generated file is well written'''
        # We have to close connection first since the Db will be recreated. It's
        # an issue for windows.
        self.conn.close()
        import_file_name = 'data/import_subscriber_test.txt'
        importer = subscriber_importer.SubscriberImporter(import_file_name)
        importer.do_truncate_import()
        # I reopen conn and cursor because I don't know what to do with my
        # teardown method !
        self.conn = sqlite3.Connection('../databases/test.db')
        self.cursor = self.conn.cursor()

        self.exporter.do_export()

        file_pointer = codecs.open(self.test_file, 'r', 'utf-8')
        line = file_pointer.readline()
        file_pointer.close()
        self.assertTrue(line is not None)

        splitted_line = line.split('\t')
        self.assertEquals(splitted_line[2], u'ANNE DEBELLE')
        self.assertEquals(splitted_line[3], u'')
        self.assertEquals(splitted_line[4], u'')
        self.assertEquals(splitted_line[5], u'RUE DUPRE 63')
        self.assertEquals(splitted_line[6], u'BRUXELLES 1090')
        self.assertEquals(splitted_line[7], u'')
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
        file_pointer = open(self.test_file, 'r')
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
        file_pointer = codecs.open(self.test_file, 'r', 'utf-8')
        line = file_pointer.readline()
        file_pointer.close()

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

    def test_address_splitted_in_3(self):
        '''In the db, the address is stored in 2 fields (address and
        address_addition). Routage file split the address on 3 fields. We can
        translate the 2 db fields to use the 3 * 32 chars availables'''
        subscriber = Subscriber()
        subscriber.address = '3456713 avenue de la mediterranee en absence de lol'
        subscriber.address_addition = 'avec plein de choses dedans'
        subscriber.save()
        line = self.__read_fist_line_of_export()
        splitted_line = line.split('\t')
        self.assertEqual(splitted_line[5], '3456713 AVENUE DE LA')
        self.assertEqual(splitted_line[6], 'MEDITERRANEE EN ABSENCE DE LOL')
        self.assertEqual(splitted_line[7], 'AVEC PLEIN DE CHOSES DEDANS')

    def test_real_address_splitted_in_3(self):
        """Test for address splitting but with a real address from the export
        file"""
        subscriber = Subscriber()
        subscriber.address = 'QUARTIER LES BIZETS'
        subscriber.address_addition = 'PLAN DES PENNES'
        subscriber.save()
        line = self.__read_fist_line_of_export()
        splitted_line = line.split('\t')
        # If field one is less than 32 char and field 2 less than 32 char, no
        # reorg
        self.assertEqual(splitted_line[5], 'QUARTIER LES BIZETS')
        self.assertEqual(splitted_line[6], 'PLAN DES PENNES')

    def __read_fist_line_of_export(self):
        self.exporter.do_export()
        file_pointer = codecs.open(self.test_file, 'r', 'utf-8')
        line = file_pointer.readline()
        file_pointer.close()
        return line

    def test_non_ascii_char(self):
        subscriber = Subscriber()
        subscriber.lastname = u'Toto°°'
        subscriber.issues_to_receive = 1
        subscriber.save()
        line = self.__read_fist_line_of_export()
        self.assertTrue(line is not None)

    def test_5_digit_post_code(self):
        """Checks that the exported post_code is always written with 5 digits,
        even if the first one is 0."""
        subscriber = Subscriber()
        subscriber.post_code = 1300
        subscriber.save()
        line = self.__read_fist_line_of_export()
        splitted_line = line.split('\t')
        self.assertEqual(splitted_line[8], '01300')

    def test_noexception_with_emtpy_string_postcode(self):
        """Test that former empty postcode leads to no export error exception"""
        subscriber = Subscriber()
        subscriber.lastname = 'toto'
        subscriber.post_code = ''
        subscriber.save()
        line = self.__read_fist_line_of_export()
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
        line = self.__read_fist_line_of_export()
        splitted = line.split('\t')
        self.assertEqual('CHEZ LULU', splitted[5])
        self.assertEqual('14 RUE LALALA', splitted[6])

    def tearDown(self):
        '''Delete generated file'''
        os.remove(self.test_file)
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
