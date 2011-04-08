#!/usr/bin/env python
'''Ce script lance un import dans ga.db'''
from subscriber_importer import SubscriberImporter

def main():
    importer = SubscriberImporter('../doc_externes/abonnements.csv')
    importer.do_truncate_import()
if __name__ == '__main__':
    main()

