#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import os

def create_db(dbfile):
	'''Create the radio stations database'''

	if(os.path.isfile(dbfile)):
		print "db file %s already exists" % dbfile
		return
	
	con = lite.connect(dbfile)

	with con:

		# this query checks for a tables existence
		'''SELECT name FROM sqlite_master WHERE type='table' AND name='table_name'''
		
		cur = con.cursor()

		# for sqlite dont specify primary keys as NOT NULL
		# see http://stackoverflow.com/questions/11490100/no-autoincrement-for-integer-primary-key-in-sqlite3

        cur.execute('''CREATE TABLE Station(
		Id INTEGER PRIMARY KEY AUTOINCREMENT, 
		Name TEXT NOT NULL''')
		
		cur.execute('''CREATE TABLE Stream(
		Id INTEGER PRIMARY KEY AUTOINCREMENT, 
		Uri TEXT NOT NULL
        FOREIGN KEY(StationId) REFERENCES Station(Id))''')

		print "Database has been created"
	