#!/usr/bin/env python

"""This script updates the database if needed at startup"""

import gaabo_conf
import sqlite3
import os

def run():
    updater = DbUpdater()
    updater.add_mail_sent_col()

class DbUpdater(object):
    def __init__(self):
        db_path = os.path.join(gaabo_conf.db_directory, gaabo_conf.db_name)
        self.conn = sqlite3.Connection(db_path)
        self.cur = self.conn.cursor()

    def add_mail_sent_col(self):
        try:
            self.cur.execute("SELECT mail_sent FROM subscribers WHERE 0 = 1")
        except sqlite3.OperationalError:
            self.cur.execute("ALTER TABLE subscribers ADD COLUMN mail_sent INTEGER")

        self.cur.execute("UPDATE subscribers SET mail_sent = 0 WHERE mail_sent IS NULL")
        self.conn.commit()

