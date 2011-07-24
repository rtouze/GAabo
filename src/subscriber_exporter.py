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

class AbstractExporter(object):
    """Object parent of all the exporters. It's useless to instanciate it"""
    def __init__(self, file_path):
        self.db_file = os.path.join(gaabo_conf.db_directory, gaabo_conf.db_name)
        self.file_pointer = codecs.open(file_path, 'w', 'utf-8')
        self.conn = sqlite3.Connection(self.db_file)

    def close_resources(self):
        """Close resources used to generate the file"""
        self.conn.close()
        self.file_pointer.close()

class RoutageExporter(AbstractExporter):
    """This class exports the DB in the format expected by the routing service.
    Only the subscribers that have issues to receive are exported. It works for
    regular and special issues."""

    OUTPUT_LEFT_PADDING = 2
    OUTPUT_RIGHT_PADDING = 6
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
        AbstractExporter.__init__(self, file_path)
       

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
        cursor = self.conn.cursor()
        try:
            result = cursor.execute(self.query)
            for row in result:
                line = self.generate_output_line(row)
                self.file_pointer.write('\t'.join(line) + '\n')
        except:
            print 'ERROR: Exception caught\n\t%s' % sys.exc_info()[1]
        else:
            self.close_resources()

    def generate_output_line(self, sql_row):
        """Generate a line as a list from the list sql_row extracted from the
        database"""
        line = []
        line.extend(['']*self.OUTPUT_LEFT_PADDING)
        line.append(self.format_string(sql_row[0][0:32]))
        line.append(self.format_string(sql_row[1][0:20]))
        line.append(self.format_string(sql_row[2][0:32]))
        line.append(self.format_string(sql_row[3])[0:32])
        line.append(self.format_string(sql_row[4])[0:32])
        line.append(self.format_string(sql_row[5])[0:32])
        postcode = self.format_postcode(sql_row[6])
        line.append(postcode[0:5])
        line.append(self.format_string(sql_row[7][0:26]))
        line.extend(['']*self.OUTPUT_RIGHT_PADDING)
        return line

    def format_string(self, string):
        """Remove non ascii chars and set string to uppercase"""
        new_string = unicodedata.normalize('NFKD', unicode(string))
        new_string = ''.join([c for c in new_string if not unicodedata.combining(c)])
        new_string = new_string.encode('ascii', 'ignore')
        return new_string.upper()

    def format_postcode(self, postcode):
        """Format the post code as a 5 digit string"""
        if (unicode(postcode).isdigit() and postcode != 0):
            return '%05d' % postcode
        else:
            return ''

#####

class ReSubscribeExporter(AbstractExporter):
    """This class extact a CSV file for the re6subscribing mailing campaign"""

    QUERY = """SELECT firstname, lastname, company, address, address_addition,
    post_code, city FROM subscribers WHERE issues_to_receive = 0"""

    def __init__(self, file_path):
        """This constructor open a file descriptor to realize the export"""
        AbstractExporter.__init__(self, file_path)

    def do_export(self):
        """Perform the export in the file given as parameter of object
        constructor"""
        self._write_header()
        self._write_body()
        self.close_resources()

    def _write_header(self):
        """Write header line in export file"""
        header = u'Destinataire;Adresse;Complement Adresse;' + \
                u'Code Postal;Ville / Pays\n'
        self.file_pointer.write(header)

    def _write_body(self):
        """Write the body of the export file"""
        self.conn = sqlite3.Connection(self.db_file)
        for row in self._execute_query():
            self._write_in_file(row)

    def _execute_query(self):
        """Execute the query that provides the data to the export file"""
        cursor = self.conn.cursor()
        return cursor.execute(self.QUERY)

    def _write_in_file(self, row):
        """Write a data row in the file"""
        line = []
        line.append(self.__get_recipient(row))
        line.append(self.__get_address(row))
        line.append(self.__get_address_addition(row))
        line.append(self.__get_post_code(row))
        line.append(self.__get_city(row))
        self.file_pointer.write(';'.join(line) + '\n') 

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

class EmailExporter(AbstractExporter):
    QUERY = """SELECT email_address
    FROM subscribers
    WHERE email_address != ''
    AND issues_to_receive = 0
    AND hors_serie1 = 0"""

    def __init__(self, file_name):
        AbstractExporter.__init__(self, file_name)

    def do_export(self):
        cursor = self.conn.cursor()
        result = cursor.execute(self.QUERY)
        file_content = []
        for row in result:
            file_content.append(row[0].lower())

        if file_content != []:
            self.file_pointer.write(','.join(file_content) + '\n')

        self.close_resources()

def date_string_from_iso(iso_date_string):
    if iso_date_string is not None:
        items = iso_date_string.split('-')
        items.reverse()
        return '/'.join(items)
    else:
        return None
