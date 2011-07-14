#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''This module contains the exporter classes to generate dumps of the DB for
routage, checks,...'''

import os
import sqlite3
import sys
import codecs
import unicodedata
import gaabo_conf

class RoutageExporter(object):
    """This class exports the DB in the format expected by the routing service.
    Only the subscribers that have issues to receive are exported. It works for
    regular and special issues."""

    ROUTAGE_ADDRESS_FIELDS_LEN = 32
    QUERY_BASE = """SELECT
            lastname,
            firstname,
            company,
            name_addition,
            address,
            address_addition,
            post_code,
            city
            FROM subscribers
            WHERE %s > 0"""

    def __init__(self, file_path):
        """Init method open a file with ascii encoding, expected by routing
        service."""
        self.db_file = os.path.join(gaabo_conf.db_directory, gaabo_conf.db_name)
        self.file_pointer = codecs.open(file_path, 'w', 'ascii')

    def do_export(self):
        '''Export method to build a routage file for regular issue sending'''
        self.query = self.get_regular_issue_query()
        self.export_common()

    def do_export_special_issue(self):
        '''Export method for special issues that are not decremented from
        issues_to_receive field'''
        self.query = self.get_special_issue_query()
        self.export_common()

    def get_regular_issue_query(self):
        """Generate the sql query to export routage file for special issue"""
        field = 'issues_to_receive'
        query = self.QUERY_BASE % field
        return query

    def get_special_issue_query(self):
        """Generate the sql query to export routage file for special issue"""
        field = 'hors_serie1'
        query = self.QUERY_BASE % field
        return query

    def export_common(self):
        '''Common code to export for routage service'''
        conn = sqlite3.Connection(self.db_file)
        cursor = conn.cursor()
        try:
            result = cursor.execute(self.query)
            for row in result:
                #TODO verifier avec les donnees pk j'ai pris le name_addition
                reformatted_address = self.format_address(row)
                line = []
                line.append('')
                line.append('')
                line.append(self.format_string(row[0][0:32]))
                line.append(self.format_string(row[1][0:20]))
                line.append(self.format_string(row[2][0:32]))
                line.append(reformatted_address[0][0:32])
                line.append(reformatted_address[1][0:32])
                line.append(reformatted_address[2][0:32])
                #TODO
                if (unicode(row[6]).isdigit() and row[6] != 0):
                    postcode = '%05d' % row[6] 
                else:
                    postcode = ''
                line.append(postcode[0:5])
                line.append(self.format_string(row[7][0:26]))
                line.append('')
                #TODO celle-ci doit etre le mode d'expedition
                line.append('')
                line.append('')
                line.append('')
                line.append('')
                line.append('')
                self.file_pointer.write('\t'.join(line) + '\n')
        except:
            print 'ERROR: Exception caught\n\t%s' % sys.exc_info()[1]
        else:
            cursor.close()
            conn.close()
            self.file_pointer.close()

    def format_string(self, string):
        '''Remove non ascii chars and set string to uppercase'''
        new_string = unicodedata.normalize('NFKD', unicode(string))
        new_string = ''.join([c for c in new_string if not unicodedata.combining(c)])
        new_string = new_string.encode('ascii', 'ignore')
        return new_string.upper()

    def format_address(self, row):
        '''Put address in 3 32 char length token instead of 2'''
        if len(row[4]) <= 32 and len(row[5]) <= 32:
            return [self.format_string(row[4]), self.format_string(row[5]), '']

        formatted_address = ['', '', '']
        long_address = ' '.join([row[4], row[5]])
        tokens = long_address.split()
        i = 0
        for token in tokens:
            tested_triplet = (formatted_address, i, token)
            if ( self.is_room_left_in_address_field(tested_triplet)):
                current = formatted_address[i]
                formatted_address[i] = ' '.join([current, self.format_string(token)])
            else:
                i += 1
                formatted_address[i] = self.format_string(token)
        for i in xrange(0, 2):
            formatted_address[i] = formatted_address[i].strip()
        return formatted_address

    def is_room_left_in_address_field(self, triplet):
        '''test if we can add an address part to current field. See code bellow
        to know what is triplet'''
        field_list, index, token_to_add = triplet
        return (
                len(field_list[index]) + len(token_to_add)
                <= self.ROUTAGE_ADDRESS_FIELDS_LEN
                and index < 3
                )

#####

class ReSubscribeExporter(object):
    """This class extact a CSV file for the re6subscribing mailing campaign"""

    QUERY = """SELECT firstname, lastname, company, address, address_addition,
    post_code, city FROM subscribers WHERE issues_to_receive = 0"""

    def __init__(self, file_path):
        """This constructor open a file descriptor to realize the export"""
        self.db_file = os.path.join(gaabo_conf.db_directory, gaabo_conf.db_name)
        self.export_file = codecs.open(file_path, 'w', 'utf-8')
        self.conn = None

    def do_export(self):
        """Perform the export in the file given as parameter of object
        constructor"""
        self.__write_header()
        self.__write_body()
        self.__close_resources()

    def __write_header(self):
        """Write header line in export file"""
        header = u'Destinataire;Adresse;Complement Adresse;' + \
                u'Code Postal;Ville / Pays\n'
        self.export_file.write(header)

    def __write_body(self):
        """Write the body of the export file"""
        self.conn = sqlite3.Connection(self.db_file)
        for row in self.__execute_query():
            self.__write_in_file(row)

    def __execute_query(self):
        """Execute the query that provides the data to the export file"""
        cursor = self.conn.cursor()
        return cursor.execute(self.QUERY)

    def __write_in_file(self, row):
        """Write a data row in the file"""
        line = []
        line.append(self.__get_recipient(row))
        line.append(self.__get_address(row))
        line.append(self.__get_address_addition(row))
        line.append(self.__get_post_code(row))
        line.append(self.__get_city(row))
        self.export_file.write(';'.join(line) + '\n') 

    def __get_recipient(self, row):
        """Extract recipient field from a data row"""
        firstname = row[0].upper()
        lastname = row[1].upper()
        company = row[2].upper()

        if lastname == '' and company != 0:
            return company
        elif company != '':
            return '%s, POUR %s %s' % (company, firstname, lastname)
        else:
            return ' '.join([firstname, lastname, company]).strip()

    def __get_address(self, row):
        return row[3].upper()

    def __get_address_addition(self, row):
        return row[4].upper()

    def __get_city(self, row):
        return row[6].upper()

    def __get_post_code(self, row):
        postcode = row[5]
        if postcode != 0:
            return str(postcode)
        else:
            return ''

    def __close_resources(self):
        """Close every resource needed by the object"""
        self.conn.close()
        self.export_file.close()

#####

class CsvExporter(object):
    """This class allows to export the whole database as a CSV"""

    QUERY = """SELECT firstname, lastname, company, city,
    issues_to_receive, hors_serie1,
    subscription_price, membership_price, subscription_date
    FROM subscribers"""

    SEPARATOR = ';'
    EOL = '\r\n'

    def __init__(self, file_name):
        self.export_file = codecs.open(file_name, 'w', 'utf-8')

    def do_export(self):
        self.write_header()
        self.write_rows()
        self.close_resources()

    def write_header(self):
        header_list = []
        header_list.append('nom')
        header_list.append(u'société')
        header_list.append('ville/pays')
        header_list.append(u'numeros à recevoir')
        header_list.append(u'HS à recevoir')
        header_list.append('prix abonnement')
        header_list.append('prix cottisation')
        header_list.append('date abonnement')

        self.print_list(header_list)

    def print_list(self, list_to_print):
        self.export_file.write(self.SEPARATOR.join(list_to_print))
        self.export_file.write(self.EOL)

    def write_rows(self):
        for row in self.get_rows():
            self.print_current(row)

    def get_rows(self):
        db_file = os.path.join(gaabo_conf.db_directory, gaabo_conf.db_name)
        self.conn = sqlite3.Connection(db_file)
        cursor = self.conn.cursor()
        return cursor.execute(self.QUERY)

    def print_current(self, row):
        printed_row_array = []
        printed_row_array.append(unicode(' '.join([row[0], row[1]])))
        printed_row_array.append(unicode(row[2]))
        printed_row_array.append(unicode(row[3]))
        printed_row_array.append(unicode(row[4]))
        printed_row_array.append(unicode(row[5]))
        printed_row_array.append(unicode(row[6]))
        printed_row_array.append(unicode(row[7]))
        printed_row_array.append(date_string_from_iso(row[8]))

        self.print_list(printed_row_array)

    def close_resources(self):
        self.export_file.close()
        self.conn.close()

def date_string_from_iso(iso_date_string):
    if iso_date_string is not None:
        items = iso_date_string.split('-')
        items.reverse()
        return '/'.join(items)
    else:
        return None
