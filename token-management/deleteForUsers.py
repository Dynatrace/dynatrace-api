#!/usr/bin/env python3

# developed and tested with python 3.7.1

import sys
import requests

# CONFIGURATION
secret = "xxxxx" #the token management token secret
environment = "xxxxx" # your environment base url
userSuffix = "ruxit.com"
# END CONFIGURATION

tokenBaseUrl = "https://" + environment + "/api/v1/tokens"

tokenIds = requests.get(tokenBaseUrl + '?permissions=InstallerDownload&Api-Token=' + secret)

#this should catch most wrong url/secret issues
if tokenIds.status_code != 200:
	sys.exit('Request failed, error code: {}'.format(tokenIds.status_code))

for tokenId in tokenIds.json()['values']:
	tokenIdUrl = tokenBaseUrl + "/" + tokenId['id']+ "?Api-Token=" + secret
	tokenMetadata = requests.get(tokenIdUrl)
	jsonMetaData = tokenMetadata.json()
	
	if jsonMetaData['userId'].endswith(userSuffix):
		requests.delete(tokenIdUrl)
		print ('Deleted token with name {}, creator was {}'.format(jsonMetaData['name'], jsonMetaData['userId']))