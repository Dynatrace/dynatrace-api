"""
Example script for fetching given Dynatrace config list items and store them on disk. 
"""
import requests, ssl, os, sys, json

ENV = 'https://<YOUR_ENVIRONMENT>.live.dynatrace.com'
TOKEN = '<YOUR_API_TOKEN>'
HEADERS = {'Authorization': 'Api-Token ' + TOKEN}
PATH = os.getcwd()

def save(path, file, content):
	if not os.path.isdir(PATH + path): 
		os.makedirs(PATH + path)
	with open(PATH + path + "/" + file, "w", encoding='utf8') as text_file:
		text_file.write("%s" % json.dumps(content))

def saveList(list_type):
	try:
		r = requests.get(ENV + '/api/config/v1/' + list_type, headers=HEADERS)
		print("%s save list: %d" % (list_type, r.status_code))
		res = r.json()
		for entry in res['values']:
			print(entry['id'])
			tr = requests.get(ENV + '/api/config/v1/' + list_type + '/' + entry['id'], headers=HEADERS)
			save('/api/config/v1/' + list_type + '/', entry['id'], tr.json())
	except ssl.SSLError:
		print("SSL Error")


def main():
	saveList('managementZones')

if __name__ == '__main__':
	main()
