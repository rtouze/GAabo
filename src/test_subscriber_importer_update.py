#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test module for update import feature"""

import unittest

import gaabo_conf
from subscriber import Subscriber
from subscriber_importer import SubscriberImporter
from gaabo_exploit_db import SqliteDbOperator

class TestSubscriberImporterUpdate(unittest.TestCase):
    """Testing class for the feature"""

    def test_not_updated_subscriber(self):
        """Test that the subscriber that should not be updated is still
        there."""
        foobar = Subscriber.get_subscribers_from_lastname('foo')[0]
        self.assertEqual('foo', foobar.lastname)
        self.assertEqual('bar', foobar.firstname)

    def test_updated_subscriber(self):
        """Test that the subscriber in the db is updated"""
        subs_list = Subscriber.get_subscribers_from_lastname('feugere')
        self.assertEqual(len(subs_list), 1)
        feugere = subs_list[0]
        self.assertEqual(feugere.address, '67 rue de la raffiniere')

    def test_second_email_subscriber_not_modified(self):
        """Test that the other subscriber with the same email than EF is not
        modified during the import. Only the first occurence is modified."""
        charley = Subscriber.get_subscribers_from_lastname('magne')[0]
        self.assertFalse(charley.address)


def main():
    """Main treatment encapsulation"""
    __create_db()
    __put_test_data_in_db()
    __import_data()

    unittest.main()

def __create_db():
    gaabo_conf.db_name = 'test.db'
    db_ex = SqliteDbOperator()
    db_ex.remove_db()
    db_ex.create_db()

def __put_test_data_in_db():
    __create_dummy_user()
    __create_user_in_file()
    __create_duplicate_email()

def __create_dummy_user():
    sub = Subscriber()
    sub.lastname = 'foo'
    sub.firstname = 'bar'
    sub.save()

def __create_user_in_file():
    sub = Subscriber()
    sub.lastname = 'Feugere'
    sub.firstname = 'Emilie'
    sub.email_address = 'xavier.gicqueau@club-internet.fr'
    sub.save()

def __create_duplicate_email():
    sub = Subscriber()
    sub.firstname = 'charle'
    sub.lastname = 'magne'
    sub.email_address = 'xavier.gicqueau@club-internet.fr'
    sub.save()

def __import_data():
    import_file_name = 'data/import_subscriber_test.txt'
    importer = SubscriberImporter(import_file_name)
    importer.do_update_import()

if __name__ == '__main__':
    main()
