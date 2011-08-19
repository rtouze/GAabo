#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module extract the email list of subcribers that have no issues to receive."""

import subscriber_exporter

def main():
    file_name = '../email_resubscription.txt'
    print u'Extraction des abonnés à renouveler dans %s...' % file_name

    exporter = subscriber_exporter.EmailExporter(file_name)
    exporter.do_export()

    print 'Fait.'

if __name__ == '__main__':
    main()
