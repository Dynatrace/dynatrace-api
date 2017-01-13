#
# Script for automatic tagging of monitored components within Dynatrace.
#
import requests

# Enter your own environment id and API key token here 
YOUR_ENV_ID = '';
YOUR_API_TOKEN = '';
WHAT = 'applications';

# Configure a list of strings and tags that are then used to automatically tag monitored components.
# Find details on metric types within our Dynatrace API help documentation here:
# https://help.dynatrace.com/api-documentation/v1/
CONFIG = [ { 'containsString' : 'ser', 'tags': ['serTest', 'serTest2']},
           { 'containsString' : 'sland', 'tags': ['wol']}
		 ]

def tagComponent(entityId, tags):
	#print(tags);	 
	headers = {'Content-Type' : 'application/json', 'Authorization' : 'Api-Token ' + YOUR_API_TOKEN };
	url = 'https://' + YOUR_ENV_ID + '.live.dynatrace.com/api/v1/entity/' + WHAT + '/' + entityId;
	r = requests.post(url, json=tags, headers=headers);
	if r.status_code == 204:
		print('Ok');
	elif r.status_code == 401:
		print('Dynatrace authentication failed, please check your API token!');
	elif r.status_code == 400:
		print('Wrong timeseriesid, aggregation type or entity combination, please check Dynatrace API help for valid combinations!');
	else:
		print('Error ' + str(r));	 
		 
		 
headers = {'Content-Type' : 'application/json', 'Authorization' : 'Api-Token ' + YOUR_API_TOKEN };
url = 'https://' + YOUR_ENV_ID + '.live.dynatrace.com/api/v1/entity/' + WHAT;
r = requests.get(url, headers=headers);
if r.status_code == 200:
	j = r.json();
	count = 1;
	for component in j:
		tags = { 'tags' : [] };
		for conf in CONFIG:
			if conf['containsString'] in component['displayName']:
				for tag in conf['tags']:
					tags['tags'].append(tag);
		print(str(count) + ' / ' + str(len(j)) + '   ' + component['displayName']);
		if len(tags['tags']) > 0:
			tagComponent(component['entityId'], tags);
		count += 1;
elif r.status_code == 401:
    print('Dynatrace authentication failed, please check your API token!');
elif r.status_code == 400:
    print('Bad request!');
else:
    print('Error ' + str(r));
