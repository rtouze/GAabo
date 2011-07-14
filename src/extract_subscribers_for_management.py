#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subscriber_exporter import CsvExporter

def main():
    file_name = '../subscriber_list.csv'
    print u'Extraction des abonnés dans %s...' % file_name

    exporter = CsvExporter(file_name)
    exporter.do_export()

    print 'Fait.'

if __name__ == '__main__':
    main()
