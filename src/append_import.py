#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script run and import in ga.db in append mode."""

import sys
from subscriber_importer import SubscriberImporter


def main():
    """Main fonction that import the file put as a parameter"""
    file_name = sys.argv[1]

    print 'Import du fichier %s.' % file_name
    importer = SubscriberImporter(file_name)
    importer.do_append_import()
    print 'Import termine'

if __name__ == '__main__':
    main()
