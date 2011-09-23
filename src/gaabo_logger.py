#!/usr/bin/env python
'''Logger module for gaabo appli'''

import logging

class Logger(object):

    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        format_string ="%(asctime)s - %(name)s - %(levelname)s - %(message)s" 
        self.formatter = logging.Formatter(format_string)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)


class ConsoleLogger(Logger):
    def __init__(self, logger_name):
        Logger.__init__(self, logger_name)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

class FileLogger(Logger):
    def __init__(self, logger_name, file_name):
        Logger.__init__(self, logger_name)
        handler = logging.FileHandler(file_name)
        handler.setLevel(logging.INFO)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

class TestLogger(Logger):
    def __init__(self, logger_name):
        Logger.__init__(self, logger_name)

