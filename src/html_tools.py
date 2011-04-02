#!/usr/bin/env python
'''This package provides tool to build html standalone pages'''

css_style = '''
        body {
            font-size: 10pt;
            font-family: sans-serif;
            margin: 15px;
        }
        table {
            font-size: 10pt;
            font-family: sans-serif;
            border-style: solid;
            border-color: black;
            border-width: 1px;
            border-collapse: collapse;
        }
        td, th {
            border-style: solid;
            border-color: black;
            border-width: 1px;
            padding: 2px;
        }
        '''

__unformatted_html_header = '''
        <html>
        <head><title>%s</title></head>
        <style type="text/css">%s
        </style>
        <body>
        '''

html_footer = '''
            </body>
        </html>
        '''

def html_header(title):
    '''Returns the html header, with css style and page title'''
    return __unformatted_html_header % (title, css_style)
