#!/usr/bin/env python
# -*- coding: utf-8 *-*
"""Test case for CSV exporter object from subscriber exporter module."""

import unittest
import os
import codecs
import sqlite3
import datetime

import subscriber_importer
import gaabo_conf
from subscriber_exporter import CsvExporter
from subscriber import Subscriber

class CsvExporterTest(unittest.TestCase):
    """Test class for the CsvExporter from subscriber_exporter module"""
    #TODO : I should create a hierarchy with all exporter tests

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
        expected_head = 'nom;ville/pays;prix abonnement;prix cottisation;' + \
        'date abonnement\r\n'
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
        expected_line = 'John Doe;Rouen;20.0;30.0;12/07/2011\r\n'
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

    def tearDown(self):
        os.remove(self.test_file)
        self.cursor.close()
        self.conn.close()

    # TODO test avec une date genre 200

def save_basic_subscriber():
    sub = Subscriber()
    sub.lastname = 'Doe'
    sub.firstname = 'John'
    sub.city = 'Rouen'
    sub.subscription_price = 20
    sub.membership_price = 30
    sub.subscription_date = datetime.date(2011, 07, 12)
    sub.save()

def save_accent_subscriber():
    sub = Subscriber()
    sub.lastname = u'Yé'
    sub.firstname = u'Bébé'
    sub.save()

if __name__ == '__main__':
    unittest.main()
