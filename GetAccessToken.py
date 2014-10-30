#!/usr/bin/env python

import facebook 
#import requests

FACEBOOK_APP_ID = "1509848215939740"
FACEBOOK_APP_SECRET = "7dd9773ab33433574ac6423cc5d8ff63"

def main():
	access_token = facebook.get_app_access_token(FACEBOOK_APP_ID,FACEBOOK_APP_SECRET)
	print access_token


if __name__ == "__main__":
    main()

