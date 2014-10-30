#! /usr/bin/python

import psycopg2
import sys

con = None

try:
	con = psycopg2.connect("dbname = 'testdb'")
	cur = con.cursor()

	cur.execute("CREATE TABLE Player ( Name VARCHAR(80),Team VARCHAR(50))")
	con.commit()

except psycopg2.DatabaseError, e:
	
	if con:
		con.rollback()
	print 'Error %s' % e    
	sys.exit(1)
finally:
    if con:
        con.close()