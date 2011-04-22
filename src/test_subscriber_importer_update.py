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
        self.assertEqual(len(subs_list), 1, 'Bad size for sub_list')
        feugere = subs_list[0]
        self.assertEqual(feugere.address, '67 rue de la raffiniere')

    # TODO test with more than one occurence
    # TODO test with empty name and a company
    # TODO test with empty name and more than once company

def main():
    """Main treatment encapsulation"""
    gaabo_conf.db_name = 'test.db'
    db_ex = SqliteDbOperator()
    db_ex.remove_db()
    db_ex.create_db()
    import_file_name = 'data/import_subscriber_test.txt'
    sub = Subscriber()
    sub.lastname = 'foo'
    sub.firstname = 'bar'
    sub.save()
    sub = Subscriber()
    sub.lastname = 'Feugere'
    sub.firstname = 'Emilie'
    importer = SubscriberImporter(import_file_name)
    importer.do_update_import()

    unittest.main()

if __name__ == '__main__':
    main()
