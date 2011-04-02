#!/usr/bin/env python
'''This module contains the exporter classes to generate dumps of the DB for
routage, checks,...'''

import os
import sqlite3
import sys
import codecs
import unicodedata
import gaabo_conf
import gaabo_constants
import html_tools

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
                line.append(reformatted_address[0])
                line.append(reformatted_address[1])
                line.append(reformatted_address[2])
                line.append(unicode(row[6])[0:5])
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

class HtmlExporter(object):
    def __init__(self, file_name):
        self.db_file = os.path.join(gaabo_conf.db_directory, gaabo_conf.db_name)
        self.file_desc = codecs.open(file_name, 'w', 'utf-8')

    def do_export(self):
        self.__init_file()
        self.file_desc.write('<tr>\n')
        sql_fields = [] 
        for pair in gaabo_constants.field_names:
            self.file_desc.write('<th>%s</th>\n' % pair[1])
            sql_fields.append(pair[0])
        self.file_desc.write('</tr>\n')

        sql_field_str = ', '.join(sql_fields)
        sql = 'SELECT %s FROM subscribers' % sql_field_str

        conn = sqlite3.Connection(self.db_file)
        cursor = conn.cursor()
        result = cursor.execute(sql)
        for row in result:
            self.file_desc.write('<tr>\n')
            for field in row:
                self.file_desc.write('<td>')
                self.file_desc.write(unicode(field))
                self.file_desc.write('</td>\n')
            self.file_desc.write('</tr>\n')
        cursor.close()
        conn.close()
        self.__close_file()

    def __init_file(self):
        header = html_tools.html_header('Test export html')
        header += '''<h1>Test export des donn&eacute;es</h1>\n<table>'''
        self.file_desc.write(header)

    def __close_file(self):
        footer = '''</table>\n'''
        footer += html_tools.html_footer
        self.file_desc.write(footer)
        self.file_desc.close()

if __name__ == '__main__': 
    print 'Creation du fichier test.html a partir de la base de test...'
    gaabo_conf.db_name = 'ga.db'
    exporter = HtmlExporter('ga.html')
    exporter.do_export()
    print 'Fait.'

