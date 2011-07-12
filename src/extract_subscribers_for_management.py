#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subscriber_exporter import CsvExporter

def main():
    print u'Extraction des abonnés dans ../subscriber_list.csv...'

    exporter = CsvExporter('../resubscription.csv')
    exporter.do_export()

    print 'Fait.'

if __name__ == '__main__':
    main()
