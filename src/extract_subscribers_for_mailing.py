#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subscriber_exporter import ReSubscribeExporter

def main():
    print u'Extraction des abonnés à renouveler dans ../resubscription.csv...'
    print 'Fait.'

    exporter = ReSubscribeExporter('../resubscription.csv')
    exporter.do_export()

if __name__ == '__main__':
    main()
