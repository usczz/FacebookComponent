#!/usr/bin/env python

import facebook
import sys
from datetime import datetime
import calendar
import string
import requests
import inspect

class Authorizer:
	"""Get access token from Facebook
	object = Authorizer()
	access_token = object.get_access_token()
	"""

	FACEBOOK_APP_ID = "1509848215939740"
	FACEBOOK_APP_SECRET = "7dd9773ab33433574ac6423cc5d8ff63"

	def __init__(self):
		self.access_token = facebook.get_app_access_token(self.FACEBOOK_APP_ID,self.FACEBOOK_APP_SECRET)

	def get_access_token(self):
		return self.access_token

class SearchParser:
	"""Get search result"""
	def __init__(self, graph,name,team):
		response = graph.get_object("search?q=%s&type=page" % name)
		self.data = response['data']
		self.counter = 0

	def isEmpty(self):
		if self.counter < len(self.data):
			return False
		else:
			return True

	def pop(self):
		if not self.isEmpty():
			page = self.data[self.counter]
			self.counter += 1
			return page
		else:
			return None

class VerifiedPageChecker:
	"""Check whether a facebook_id is verified"""

	def __init__(self,graph,pageid):
		self.response = graph.get_object("%s?fields=is_verified" % pageid)

	def isVerified(self):
		return self.response['is_verified']

class correctPageChecker:
	"""Check whether a facebook page is correct"""
	team = None
	def __init__(self, graph):
		self.graph = graph
		self.__initKeywordList()

	def __initKeywordList(self):
		self.keyword = []
		self.keyword.append('MLS')
		self.keyword.append('mls')
		self.keyword.append('Major League Soccer')
		self.keyword.append('soccer')
		self.keyword.append('footballer')
		self.keyword.append('offical')
		self.keyword.append('OFFICIAL')
		self.keyword.append('futbolista')
		self.keyword.append('USL')
		self.keyword.append('usl')
		self.keyword.append('NASL')
		self.keyword.append('nasl')
		self.keyword.append('goal')
		#self.keyword.append('us')
		#self.keyword.append('US')

	def addKeyword(self,keyword):
		self.__addKeyword(keyword)

	def __addKeyword(self,keyword):
		self.keyword.append(keyword)

	def removeKeyword(self,keyword):
		self.__removeKeyword(keyword)

	def __removeKeyword(self,keyword):
		index = self.keyword.index(keyword)
		self.keyword.pop(index)

	def load(self,pageid,team):
		self.response = self.graph.get_object(pageid)
		if self.team != None:
			self.removeKeyword(self.team)
		self.team = team
		self.addKeyword(self.team)

	def __checkKeyword(self,str):
		for x in xrange(0,len(self.keyword)):
			if str.find(self.keyword[x]) != -1:
				return True
	
	def isCorrect(self):
		if self.response.has_key('about'):
			about = self.response['about']
			if self.__checkKeyword(about):
				return True
		if self.response.has_key('description'):
			des = self.response['description']
			if self.__checkKeyword(des):
				return True
		if self.response.has_key('personal_info'):
			info = self.response['personal_info']
			if self.__checkKeyword(info):
				return True
		if self.response.has_key('username'):
			username = self.response['username']
			if self.__checkKeyword(username):
				return True
		return False
		
class pageParser:
	"""Parse information on main page"""
	def __init__(self,graph,pageid):
		self.graph = graph
		self.response = self.graph.get_object(pageid)

	def getTalkingAbout(self):
		if self.response.has_key('talking_about_count'):
			return self.response['talking_about_count']
		else:
			return None

	def getLikes(self):
		if self.response.has_key('likes'):
			return self.response['likes']
		else:
			return None

	def parse(self):
		result = {}
		likes = self.getLikes()
		if likes != None:
			result['likes'] = likes
		talking = self.getTalkingAbout()
		if talking != None:
			result['talking_about_count'] = talking
		return result

class postsParser:
	"""Parse data for status"""
	def __init__(self,graph,pageid):
		self.graph = graph
		self.pageid = pageid
		date = datetime.utcnow()
		year = date.year
		month = date.month
		if month > 6:
			year -=1
			month-=6
		else:
			month +=6
		newdate = date.replace(year=year,month=month)
		timestamp = calendar.timegm(newdate.utctimetuple())
		self.stamp = str(timestamp)
		self.limit = 25
		self.response =  self.graph.get_object(pageid+"/posts?limits="+str(self.limit))


	def getNext(self):
		if self.response.has_key('paging'):
			if self.response['paging'].has_key('next'):
				nextLink = self.response['paging']['next']
				link = str(nextLink)
				untilIndex = string.find(link,"until=")
				untilData = link[untilIndex+6:]
				if untilData < self.stamp:
					return None
				else:
					return nextLink
			else:
				return None
		else:
			return None	

	def parse(self):
		result ={}
		posts= []
		count = 0
		end = False
		pageCount = 0
		while not end:
			if not self.response.has_key('data'):
				result['count'] = count
				return result
			data = self.response['data']
			print "page#"+str(pageCount)
			for x in xrange(0,len(data)):
				print "Post#"+str(x)
				item = data[x]
				if not item.has_key('id'):
					continue
				postid = item['id']
				postAgent = postParser(self.graph,postid)
				itemdata = postAgent.parse()
				posts.append(itemdata)
				count = count+1
			link = self.getNext()
			if link == None:
				end = True
			else:
				r = requests.get(link)
				self.response = r.json()
				pageCount += 1
		result['count'] = count
		result['posts'] = posts
		return result

class postParser:
	"""get post data"""
	def __init__(self,graph,postid):
		self.graph = graph
		self.limit = 25
		self.postid = postid
		self.response = self.graph.get_object(self.postid+"/comments?summary=1&filter=toplevel&limits="+str(self.limit))
		date = datetime.utcnow()
		year = date.year
		month = date.month
		if month > 6:
			month -=6
		else:
			month+=6
			year -=1
		newdate = date.replace(year=year,month=month)
		timestamp = calendar.timegm(newdate.utctimetuple())
		self.stamp = str(timestamp)

	def getNext(self):
		if self.response.has_key('paging'):
			if self.response['paging'].has_key('cursors'):
				nextLink = self.response['paging']['next']
				link = str(nextLink)
				untilIndex = string.find(link,"until=")
				untilData = link[untilIndex+6:]
				if untilData < self.stamp:
					return None
				else:
					return nextLink
			else:
				return None
		else:
			return None	

	def parse(self):
		result = {}
		message = self.__parseMessage()
		if message != None:
			result['Status'] = message
		result['Likes'] = self.__parseLikes()
		result['Comments'] = self.__parseComments()
		return result

	def __parseComments(self):
		result = {}
		messages = []
		end = False
		while not end:
			if self.response.has_key('summary'):
				if self.response['summary'].has_key('total_count'):
					result['total_count'] = self.response['summary']['total_count']
			if self.response.has_key('data'):
				data = self.response['data']
				for x in xrange(0,len(data)):
					if data[x].has_key('message'):
						messages.append(data[x]['message'])
				end = True
		result['messages'] = messages
		return result

	def __parseLikes(self):
		r = self.graph.get_object(self.postid+"/likes?summary=1&filter=toplevel")
		if r.has_key('summary'):
			if r['summary'].has_key('total_count'):
				return r['summary']['total_count']
			else:
				return 0
		else:
			return 0

	def __parseMessage(self):
		r = self.graph.get_object(self.postid)
		if r.has_key('message'):
			return r['message']
		else:
			return None


def setEncode(code):
	"""Set default encoding for string"""
	reload(sys)
	sys.setdefaultencoding(code)



		
		