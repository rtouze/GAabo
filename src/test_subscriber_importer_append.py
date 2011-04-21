#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests the import from plain file in append mode"""

import unittest

import gaabo_conf
import subscriber_importer
from gaabo_exploit_db import SqliteDbOperator
from subscriber import Subscriber

class TestSubscriberImporterAppend(unittest.TestCase):
    """Test class that performs the test of the feature"""

    def test_former_subscriber_exists(self):
        """Test that subscriber foo bar created before import is still in the
        database."""
        foobar = Subscriber.get_subscribers_from_lastname('foo')[0]
        self.assertEquals(foobar.lastname, 'foo')

    def test_new_subscriber_exists(self):
        """Test that we can find a newly created customer"""
        feugere = Subscriber.get_subscribers_from_lastname('feugere')[0]
        self.assertEquals(feugere.lastname, 'Feugere')
        self.assertEquals(feugere.firstname, 'Emilie')

def main():
    """Creates a new test db and create subscriber foo bar in it. The info in
    the test file are then imported and unittest is run"""

    gaabo_conf.db_name = 'test.db'
    __recreate_db()
    __create_a_subscriber()
    __import_file()
    unittest.main()

def __recreate_db():
    db_ex = SqliteDbOperator()
    db_ex.remove_db()
    db_ex.create_db()

def __create_a_subscriber():
    sub = Subscriber()
    sub.lastname = 'foo'
    sub.firstname = 'bar'
    sub.save()

def __import_file():
    import_file_name = 'data/import_subscriber_test.txt'
    importer = subscriber_importer.SubscriberImporter(import_file_name)
    importer.do_append_import()

if __name__ == '__main__':
    main()

