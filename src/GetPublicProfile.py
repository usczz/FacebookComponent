#!/usr/bin/env python

import facebook
import sys
import os
import dicttoxml
from xml.dom import minidom
import psycopg2
from datetime import datetime
import calendar
import string
import requests
import inspect 

FACEBOOK_APP_ID = "1509848215939740"
FACEBOOK_APP_SECRET = "7dd9773ab33433574ac6423cc5d8ff63"

class Authorizer:

	def __init__(self,app_id,app_secret):
		self.app_id = app_id
		self.app_secret = app_secret
		self.access_token = facebook.get_app_access_token(FACEBOOK_APP_ID,FACEBOOK_APP_SECRET)

	def get_access_token(self):
		return self.access_token

class SearchParser:

	filename = 'searchResult.xml'

	def __init__(self,response):
		self.xml = dicttoxml.dicttoxml(response)
		output = open(self.filename,'w')
		output.write(self.xml)
		output.close()
		self.xmldoc = minidom.parse(self.filename)
		os.remove(self.filename)
		self.data = self.xmldoc.getElementsByTagName('data')
		self.pageList = []
		for x in xrange(0,self.data[0].childNodes.length):
			self.pageList.append(self.data[0].childNodes[x])
		self.counter = 0

	def pop(self):
		if not self.isEmpty():
			page = self.__parseItem()
			self.counter = self.counter + 1
			return page
		else:
			return None

	def __parseItem(self):
		page = {}
		category = self.pageList[self.counter].getElementsByTagName('category')
		category_data = category[0].firstChild.data.encode('ascii')
		pageid = self.pageList[self.counter].getElementsByTagName('id')
		pageid_data = pageid[0].firstChild.data.encode('ascii')
		page['id'] = pageid_data
		page['category'] = category_data
		return page

	def isEmpty(self):
		if self.counter < len(self.pageList):
			return False
		else:
			return True
			
	def Print(self):
		print self.xmldoc.toxml()

class verifiedPageChecker:
	filename = 'verifypage.xml'

	def __init__(self,response):
		self.xml = dicttoxml.dicttoxml(response)
		output = open(self.filename,'w')
		output.write(self.xml)
		output.close()
		self.xmldoc = minidom.parse(self.filename)
		os.remove(self.filename)
		self.data = self.xmldoc.getElementsByTagName('is_verified')
		self.verified = self.data[0].firstChild.data

	def Print(self):
		print self.xmldoc.toxml()

	def is_verifiedPage(self):
		if self.verified == 'true':
			return True
		else:
			return False

class correctPageChecker:
	filename = 'correctpage.xml'
	team = None
	spanish = None

	def __init__(self):
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
		self.keyword.append('us')
		self.keyword.append('US')

	def Print(self):
		print self.xmldoc.toxml()

	def addKeyword(self,keyword):
		self.__addKeyword(keyword)

	def __addKeyword(self,keyword):
		self.keyword.append(keyword)

	def removeKeyword(self,keyword):
		self.__removeKeyword(keyword)

	def __removeKeyword(self,keyword):
		index = self.keyword.index(keyword)
		self.keyword.pop(index)

	def __checkKeyword(self,str):
		for x in xrange(0,len(self.keyword)):
			if str.find(self.keyword[x]) != -1:
				return True

	def load(self,response,team,spanish):
		if self.team != None:
			self.__removeKeyword(self.team)
		if self.spanish != None:
			self.__removeKeyword(self.spanish)
		self.team = team
		self.spanish = spanish
		self.xml = dicttoxml.dicttoxml(response)
		output = open(self.filename,'w')
		output.write(self.xml)
		output.close()
		self.xmldoc = minidom.parse(self.filename)
		os.remove(self.filename)
		self.__addKeyword(team)
		self.__addKeyword(spanish)
	
	def is_correctPage(self):
		des = self.xmldoc.getElementsByTagName('description')
		about = self.xmldoc.getElementsByTagName('about')
		info = self.xmldoc.getElementsByTagName('personal_info')
		username = self.xmldoc.getElementsByTagName('username')
		if len(about) != 0:
			about_data = about[0].firstChild.data
			#print about_data
			if self.__checkKeyword(about_data):
				return True
		if len(des) != 0:
			des_data = des[0].firstChild.data
			#print des_data
			if self.__checkKeyword(des_data):
				return True
		if len(info) != 0:
			info_data = info[0].firstChild.data
			#print info_data
			if self.__checkKeyword(info_data):
				return True
		if len(username) != 0:
			name = username[0].firstChild.data
			#print name
			if name.find('official') != -1 or name.find('OFFICIAL') != -1:
				return True
		return False



class pageParser:

	filename = 'pageResult.xml'

	def __init__(self,response):
		self.xml = dicttoxml.dicttoxml(response)
		output = open(self.filename,'w')
		output.write(self.xml)
		output.close()
		self.xmldoc = minidom.parse(self.filename)
		# os.remove(self.filename)


	def __parseItem(self):
		likes = self.xmldoc.getElementsByTagName('likes')
		talking = self.xmldoc.getElementsByTagName('talking_about_count')
		identifier = self.xmldoc.getElementsByTagName('id')
		self.likes_data = likes[0].firstChild.data
		self.talking_data = talking[0].firstChild.data
		self.id = identifier[0].firstChild.data
		print self.id
		if identifier.length > 1:
			self.id = identifier[identifier.length-1].firstChild.data
		print self.id


	def parse(self):
		self.__parseItem()
		return {'id':self.id,'talking_about':self.talking_data,'likes':self.likes_data}


class postsParser:

	filename = 'postsResult.xml'


	def __init__(self,response,graph):
		self.xml =  dicttoxml.dicttoxml(response)
		output = open(self.filename,'w')
		output.write(self.xml)
		output.close()
		self.xmldoc = minidom.parse(self.filename)
		#os.remove(self.filename)
		self.graph = graph
		#print self.xmldoc.toxml()
		d = datetime.utcnow()
		y = d.year
		newd = d.replace(year=y-1)
		timestamp = calendar.timegm(newd.utctimetuple())
		self.stamp = str(timestamp)
	
	def getNext(self):
		nexts = self.xmldoc.getElementsByTagName('next')
		link = nexts[0].firstChild.data
		try:
			untilIndex = string.find(link,"until=")
			#print untilIndex
			untilData = link[untilIndex+6:]
			print untilData
			print self.stamp
			if untilData < self.stamp:
				link = None
		except Exception, e:
			print "Error %s" % e
			link = None
		finally:
			return link


	def __parse(self):
		result = {}
		posts = []
		count = 0
		flag = True
		pageCount = 0
		while flag:
			root = self.xmldoc.getElementsByTagName('root')
			# print root[0].toxml()
			if root[0].childNodes.length < 2:
		 		return result
			data = root[0].childNodes[1]
			print "Page#"+str(pageCount)
			# print data.childNodes.length
			for x in xrange(0,data.childNodes.length):
				print "Post#"+str(x)
		 		item = data.childNodes[x]
		 		postids = item.getElementsByTagName('id')
		 		if not postids.length:
		 			return None
		 		postid = postids[postids.length-1].firstChild.data
		 		postAgent = postParser(self.graph,postid)
		 		itemdata = postAgent.Parse()
		 		#print item
		 		posts.append(itemdata)
		 		count = count+1
		 # 	link = self.getNext()
		 # 	if link != None:
		 # 		r = requests.get(link)
		 # 		response = r.json()
		 # 		self.xml =  dicttoxml.dicttoxml(response)
			# 	output = open(self.filename,'w')
			# 	output.write(self.xml)
			# 	output.close()
			# 	self.xmldoc = minidom.parse(self.filename)
			# 	pageCount = pageCount+1
			# else:
			# 	flag = False
			flag = False
		result['count'] = count
		result['posts'] = posts
		return result	

	def Parse(self):
		result = self.__parse()
		return result

class postParser:
	"""docstring for postParser"""
	filename = "postResult.xml"

	def __init__(self,graph,postid):
		self.graph = graph
		self.id = postid
		d = datetime.utcnow()
		y = d.year
		newd = d.replace(year=y-1)
		timestamp = calendar.timegm(newd.utctimetuple())
		self.stamp = str(timestamp)

	
	def Parse(self):
		#get message
		result = {}
		result['Status'] = self.__parseMessage()
		result['Likes'] = self.__parseLikes()
		result['Comments'] = self.__parseComments()
		return result

	def getNext(self):
		nexts = self.xmldoc.getElementsByTagName('next')
		link = nexts[0].firstChild.data
		try:
			untilIndex = string.find(link,"until=")
			#print untilIndex
			untilData = link[untilIndex+6:]
			if untilData < self.stamp:
				link = None
		except Exception, e:
			print "Error %s" % e
			link = None
		finally:
			return link

	def __parseComments(self):
		result = {}
		messages = []
		#get total count of comments
		response = self.graph.get_object(self.id+"/comments?summary=1&filter=toplevel&limit=25")
		xml = dicttoxml.dicttoxml(response)
		output = open(self.filename,'w')
		output.write(xml)
		output.close()
		flag = True
		while flag:
			try:
				xmldoc = minidom.parse(self.filename)
				os.remove(self.filename)
				total_counts = xmldoc.getElementsByTagName('total_count')
				if len(total_counts):
					result['total_count'] = total_counts[0].firstChild.data
				else:
					result['total_count'] = None
				#get up to 250 comments in a page
				#print result['total_count']
				#print xmldoc.toxml()
				if result['total_count'] != None and result['total_count']:
					message = xmldoc.getElementsByTagName('message')
					for x in xrange(0,message.length):
						#print x
						if message[x].firstChild != None:
							messages.append(message[x].firstChild.data)
				# link = self.getNext()
				# if link !=None:
				# 	r = requests.get(link)
		 	# 		response = r.json()
		 	# 		self.xml =  dicttoxml.dicttoxml(response)
				# 	output = open(self.filename,'w')
				# 	output.write(self.xml)
				# 	output.close()
				# else:
				# 	flag = False
				flag = False
			except Exception,e:
				print "Error %s" % e
				#print response['summary']['total_count']
				result['total_count'] = response['summary']['total_count']
				data = response['data']
				for x in xrange(0,len(data)):
					messages.append(data[x]['message'])
				#result['messages'] = messages
			finally:		
				break
		result['messages'] = messages
		return result

	def __parseLikes(self):
		response = self.graph.get_object(self.id+"/likes?summary=1&filter=toplevel")
		xml = dicttoxml.dicttoxml(response)
		output = open(self.filename,'w')
		output.write(xml)
		output.close()
		xmldoc = minidom.parse(self.filename)
		os.remove(self.filename)
		total_counts = xmldoc.getElementsByTagName('total_count')
		if not len(total_counts) :
			return 0
		return total_counts[0].firstChild.data

	def __parseMessage(self):
		try:
			response = self.graph.get_object(self.id)
			xml = dicttoxml.dicttoxml(response)
			output = open(self.filename,'w')
			output.write(xml)
			output.close()
			xmldoc = minidom.parse(self.filename)
			#os.remove(self.filename)
			message = xmldoc.getElementsByTagName('message')
			if not len(message):
				return None	
			return message[message.length - 1].firstChild.data
		except Exception,e:
			print "Parse Message Error %s " % e
			return None

def setEncode(code):
	#set the default encoding to spedcific
	reload(sys)
	sys.setdefaultencoding(code)

def printResult(name,pageInfo,postInfo):
	output = open(name,'w')
	output.write('player name:'+name+'\n')
	output.write('id:'+pageInfo['id']+'\n')
	output.write('talking_about:'+pageInfo['talking_about']+'\n')
	output.write('likes:'+pageInfo['likes']+'\n')
	if not len(postInfo['posts']):
		output.close()

	output.write('posts:'+str(postInfo['count'])+'\n')
	for i in xrange(0,len(postInfo['posts'])):
		output.write('\n')
		if postInfo['posts'][i]['Status'] != None:
			output.write('post#'+str(i)+':'+postInfo['posts'][i]['Status']+'\n')
		if postInfo['posts'][i]['Likes'] != None:
			output.write('likes:'+str(postInfo['posts'][i]['Likes'])+'\n')
		try:
			output.write('Comments:\n')
			if postInfo['posts'][i]['Comments'] != None:			
				output.write('Count:'+str(postInfo['posts'][i]['Comments']['total_count'])+'\n')
				for j in xrange(0,len(postInfo['posts'][i]['Comments']['messages'])):
					if postInfo['posts'][i]['Comments']['messages'][j] != None:
						output.write(postInfo['posts'][i]['Comments']['messages'][j]+'\n')
		except Exception, e:
			print "Print Result Obafemi MartinsError %s" % e
		finally:
			output.write('\n')


	output.close()

def main():

	setEncode('utf-8')

	myAuthorizer = Authorizer(FACEBOOK_APP_ID,FACEBOOK_APP_SECRET)
	token = myAuthorizer.get_access_token()
	graph = facebook.GraphAPI(token)
	con = None
	playerList = None
	try:
		con = psycopg2.connect(database = "mydb")
		cur = con.cursor()
		cur.execute("SELECT * FROM player")
		playerList = cur.fetchall()
	except psycopg2.DatabaseError, e:
		print 'Error %s' % e
		sys.exit(1)
	finally:
		if con:
			con.close()

	for i in xrange(0,len(playerList)):
		print i
		name = playerList[i][0]
		team = playerList[i][1]
		spanish = playerList[i][2]
		idtype = "page"
		response = graph.get_object("search?q="+name+"&type="+idtype)
		searchAgent = SearchParser(response)

		pageChecker = correctPageChecker()
		correctId = None
		flag = False
		#get the correct page id
		while not searchAgent.isEmpty():
			page = searchAgent.pop()
			if page['category'] == 'Athlete':
				response = graph.get_object(page['id']+"?fields=is_verified")
				verifyChecker = verifiedPageChecker(response)
				if verifyChecker.is_verifiedPage():
					correctId = page['id']
					flag = True
					break
				else:
					response = graph.get_object(page['id'])
					pageChecker.load(response,team,spanish)
					if pageChecker.is_correctPage():
						correctId = page['id']
						flag = True
						break
		if not flag:
			print "Cann't find "+playerList[i][0]
			continue
		#print correctId
		response = graph.get_object(correctId)
		pageAgent = pageParser(response)
		pageInfo = pageAgent.parse()
		response = graph.get_object(pageInfo['id']+"/posts?limit=25")
		postAgent = postsParser(response,graph)
		postInfo = postAgent.Parse()
		print postInfo
		# #printResult(name,pageInfo,postInfo)
		if i == 0:
		  	break
	try:
		con = psycopg2.connect(database = "mydb")
		cur = con.cursor()
		cur.execute("")
	except Exception, e:
		raise e
	finally:
		pass

if __name__ == "__main__":
	main()