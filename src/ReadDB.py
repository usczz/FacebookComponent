#! /usr/bin/python

import psycopg2
import sys

con = None

try:
	con = psycopg2.connect(database = "mydb")
	cur = con.cursor()

	cur.execute("SELECT (first_name || Last_name) AS name,last_team FROM usl WHERE last_team != \'\'")
	res = cur.fetchall()
	print res

except psycopg2.DatabaseError,e:
	print 'Error %s' % e
	sys.exit(1)

finally:

	if con:
		con.close()