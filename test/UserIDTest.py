import unittest

import facebook
import sys
import os
import dicttoxml
from xml.dom import minidom
from datetime import datetime
import calendar
import string
import requests
import inspect 
import psycopg2
import myFacebook

def getUserId(name,team,graph):
	idtype = "page"
	response = graph.get_object("search?q="+name+"&type="+idtype)
	searchAgent = myFacebook.SearchParser(response)

	pageChecker = myFacebook.correctPageChecker()
	correctId = None
	flag = False
	#get the correct page id
	while not searchAgent.isEmpty():
		page = searchAgent.pop()
		if page['category'] == 'Athlete':
			response = graph.get_object(page['id']+"?fields=is_verified")
			verifyChecker = myFacebook.verifiedPageChecker(response)
			if verifyChecker.is_verifiedPage():
				correctId = page['id']
				flag = True
				break
			else:
				response = graph.get_object(page['id'])
				pageChecker.load(response,team)
				if pageChecker.is_correctPage():
					correctId = page['id']
					flag = True
				break
	if not flag:
		print "Cann't find "+name
	return correctId


class UserIDTest(unittest.TestCase):
	"""docstring for ClassName"""
	def setUp(self):
		myFacebook.setEncode('utf-8')

		self.myAuthorizer = myFacebook.Authorizer()
		self.token = self.myAuthorizer.get_access_token()
		self.graph = facebook.GraphAPI(self.token)
		# con = None
		# self.playerList = None
		# try:
		# 	con = psycopg2.connect(database = "mydb")
		# 	cur = con.cursor()
		# 	cur.execute("SELECT (first_name || last_time ) as name, last_team FROM uslUserId")
		# 	self.playerList = cur.fetchall()
		# except psycopg2.DatabaseError, e:
		# 	print 'Error %s' % e
		# 	sys.exit(1)
		# finally:
		# 	if con:
		# 		con.close()

	def test_user_id(self):
		correctid = getUserId('HughDixon','Houston Dynamo',self.graph)
				


		