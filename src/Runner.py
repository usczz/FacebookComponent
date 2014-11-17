import myFacebookV3
import psycopg2
import facebook
import sys

def main():
	myFacebookV3.setEncode('utf-8')

	authorizer = myFacebookV3.Authorizer()
	access_token = authorizer.get_access_token()
	graph = facebook.GraphAPI(access_token)

	# database cursor
	con = None
	playerList = None
	try:
		con = psycopg2.connect(database="mydb")
		cur = con.cursor()
		cur.execute("SELECT * FROM player")
		playerList = cur.fetchall()
	except Exception, e:
		print "Error %s" % e
		sys.exit(1)
	finally:
		if con:
			con.close()

	for i in xrange(0, len(playerList)):
		print i
		name = playerList[i][0]
		team = playerList[i][1]
		searchAgent = myFacebookV3.SearchParser(graph,name,team)
		pageChecker = myFacebookV3.correctPageChecker(graph)
		correctId = None
		find = False
		result = {}
		while True:
			page = searchAgent.pop()
			if page == None:
				break
			if page['category'] == 'Athlete':
				verifyAgent = myFacebookV3.VerifiedPageChecker(graph,page['id'])
				if verifyAgent.isVerified():
					correctId = page['id']
					find = True
					break
				else:
					pageChecker.load(page['id'],team)
					if pageChecker.isCorrect():
						correctId = page['id']
						find = True
						break
		if not find:
			print "Cann't find"+playerList[i][0]
			continue
		pageAgent = myFacebookV3.pageParser(graph,correctId)
		pageInfo = pageAgent.parse()
		#print pageInfo
		postAgent = myFacebookV3.postsParser(graph,correctId)
		postInfo = postAgent.parse()
		#print postInfo
		result['name'] = name
		result['id'] = correctId
		if 'likes' in pageInfo:
			result['likes'] = pageInfo['likes']
		if 'talking_about_count' in pageInfo:
			result['talking_about_count'] = pageInfo['talking_about_count']
		if 'count' in postInfo:
			result['post_count'] = postInfo['count']
		if 'posts' in postInfo:
			result['posts'] = postInfo['posts']
		print result


if __name__ == '__main__':
	main()