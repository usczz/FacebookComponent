#!/usr/bin/env python

import facebook
import sys
import dicttoxml
from xml.dom import minidom

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
		self.data = self.xmldoc.getElementsByTagName('data')
		self.pageList = []
		for x in xrange(0,self.data[0].childNodes.length-1):
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

class pageParser:

	filename = 'pageResult.xml'

	def __init__(self):
		self.__initKeywordList()

	def Print(self):
		print self.xmldoc.toxml()

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

	def addKeyword(self,keyword):
		self.keyword.append(keyword)

	def __checkKeyword(self,str):
		for x in xrange(0,len(self.keyword)-1):
			if str.find(self.keyword[x]) != -1:
				return True
        
	def load(self,response):
		self.xml = dicttoxml.dicttoxml(response)
		output = open(self.filename,'w')
		output.write(self.xml)
		output.close()
		self.xmldoc = minidom.parse(self.filename)

	def __parseItem(self):
		likes = self.xmldoc.getElementsByTagName('likes')
		talking = self.xmldoc.getElementsByTagName('talking_about_count')
		identifier = self.xmldoc.getElementsByTagName('id')
		self.likes_data = likes[0].firstChild.data
		self.talking_data = talking[0].firstChild.data
		self.id = identifier[0].firstChild.data


	def parse(self):
		self.__parseItem()
		return {'id':self.id,'talking_about':self.talking_data,'likes':self.likes_data}

	def verifyPage(self):
		des = self.xmldoc.getElementsByTagName('description')
		about = self.xmldoc.getElementsByTagName('about')
		info = self.xmldoc.getElementsByTagName('personal_info')
		username = self.xmldoc.getElementsByTagName('username')
		if len(about) != 0:
			about_data = about[0].firstChild.data
			if self.__checkKeyword(about_data):
				return True
		if len(des) != 0:
			des_data = des[0].firstChild.data
			if self.__checkKeyword(des_data):
				return True
		if len(info) != 0:
			info_data = info[0].firstChild.data
			if self.__checkKeyword(info_data):
				return True
		if len(username) != 0:
			name = username[0].firstChild.data
			if name.find('official') != -1 or name.find('OFFICIAL') != -1:
				return True
		return False

class postParser:

	filename = 'postsResult.xml'

	def __init__(self,response):
		self.xml =  dicttoxml.dicttoxml(response)
		output = open(self.filename,'w')
		output.write(self.xml)
		output.close()
		self.xmldoc = minidom.parse(self.filename)
		#print self.xmldoc.toxml()
	
	def __parse(self):
		result = []
		item = {}
		root = self.xmldoc.getElementsByTagName('root')
		#print root[0].childNodes.length
		if root[0].childNodes.length < 2:
			return result
		data = root[0].childNodes[1]
		print data.childNodes.length
		for x in xrange(0,data.childNodes.length-1):
			item = self.__parseItem(data.childNodes[x])
			print item
			result.append(item)		
		return result	

	def Parse(self):
		result = self.__parse()
		return result


	def __parseItem(self,element):
		result = {}
		#result['comments'] = self.__parseComments(element)
		result['likes'] = self.__parseLikes(element)
		result['Message'] = self.__parseMessage(element)
		return result

	def __parseComments(self,element):
		result = {}
		messages = []
		comments = element.getElementsByTagName('comments')
		if not len(comments) or comments[0].childNodes.length == 1:
			return result
		itemlist = comments[0].childNodes[1].childNodes
		result['count'] = itemlist.length
		for x in xrange(0,result['count']-1):
			message = itemlist[x].getElementsByTagName('message')
			if message[0].firstChild == None:
				messages.append(None)
				continue
			messages.append(message[0].firstChild.data)
		result['messages'] = messages
		return result

	def __parseLikes(self,element):
		likes = element.getElementsByTagName('likes')
		if not len(likes) or likes[0].childNodes.length < 2:
			return 0
		data = likes[0].childNodes[1]
		itemlist = data.childNodes
		return len(itemlist)

	def __parseMessage(self,element):
		message = element.getElementsByTagName('message')
		if not len(message):
			return None
		return message[message.length - 1].firstChild.data

def setEncode(code):
	#set the default encoding to specific
	reload(sys)
	sys.setdefaultencoding(code)

def printResult(name,pageInfo,postInfo):
	output = open(name,'w')
	output.write('player name:'+name+'\n')
	output.write('id:'+pageInfo['id']+'\n')
	output.write('talking_about:'+pageInfo['talking_about']+'\n')
	output.write('likes:'+pageInfo['likes']+'\n')
	if not len(postInfo):
		output.close() 
	for i in xrange(0,len(postInfo)-1):
		output.write('\n')
		if postInfo[i]['Message'] != None:
			output.write('post#'+str(i)+':'+postInfo[i]['Message']+'\n')
		if postInfo[i]['likes'] != None:
			output.write('likes:'+str(postInfo[i]['likes'])+'\n')
		output.write('Comments:\n')
		if postInfo[i]['comments'] != None:			
			output.write('Count:'+str(postInfo[i]['comments']['count'])+'\n')
			for j in xrange(0,postInfo[i]['comments']['count']-1):
				if postInfo[i]['comments']['messages'][j] != None:
					output.write(postInfo[i]['comments']['messages'][j]+'\n')
			output.write('\n')
	output.close()

def main():

	setEncode('utf-8')

	myAuthorizer = Authorizer(FACEBOOK_APP_ID,FACEBOOK_APP_SECRET)
	token = myAuthorizer.get_access_token()
	graph = facebook.GraphAPI(token)
	idnamelist = ['Nick Rimando']
	for i in xrange(0,len(idnamelist)):
		print i
		idname = idnamelist[i]
		idtype = "page"
		response = graph.get_object("search?q="+idname+"&type="+idtype)
		searchAgent = SearchParser(response)
		pageAgent = pageParser()
		pageInfo = {}
		postInfo = {}
		#get the correct page id
		while not searchAgent.isEmpty():
			page = searchAgent.pop()
			if page['category'] == 'Athlete':
				response = graph.get_object(page['id'])
				pageAgent.load(response)
				if pageAgent.verifyPage():
					pageInfo = pageAgent.parse()
					break
		#print pageInfo
		response = graph.get_object(pageInfo['id']+"/posts")
		postAgent = postParser(response)
		postInfo = postAgent.Parse()
		# printResult(idname,pageInfo,postInfo)



if __name__ == "__main__":
	main()