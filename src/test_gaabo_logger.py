#!/usr/bin/env python
'''Test module for gaago_logger'''

from gaabo_logger import ConsoleLogger
from gaabo_logger import FileLogger

def main():
    logger = ConsoleLogger('toto')
    logger.info('vas y loggue')
    logger.error('c est une erreur')

    logger2 = FileLogger('tata', 'tata.log')
    logger2.info('log dans fichier')

if __name__ == '__main__':
    main()
