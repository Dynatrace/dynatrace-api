#
# Script for transferring Dynatrace timeseries into AWS CloudWatch.
#
import requests, datetime, time, sched, subprocess, shlex

# Enter your own environment id and API key token here 
YOUR_ENV_ID = 'ENTER_YOUR_ENV_ID_HERE';
YOUR_API_TOKEN = 'ENTER_YOUR_API_TOKEN_HERE';

# Configure a list of monitored components you would like to transfer timeseries for.
# Please mind that the component has to support the requested tye of timeseries and
# that the timeseries also supports the requested aggregation type.
# Find details on metric types within our Dynatrace API help documentation here:
# https://help.dynatrace.com/api-documentation/v1/
CONFIG = [
		{'timeseriesId':'com.ruxit.builtin:appmethod.useractionsperminute', 'aggregation':'COUNT', 'entities':['APPLICATION_METHOD-8FBD978961794991', 'APPLICATION_METHOD-66A8C6277F0B8186']},
		{'timeseriesId':'com.ruxit.builtin:host.mem.used', 'aggregation':'AVG', 'entities':['HOST-DE6F9EC80D4D7C58']}
		]

scheduler = sched.scheduler(time.time, time.sleep)

def export_metric(name):
	scheduler.enter(360, 1, export_metric, ('first',))
	for conf in CONFIG:
		print('Pull timeseries ' + conf['timeseriesId']);
		headers = {'Content-Type' : 'application/json', 'Authorization' : 'Api-Token ' + YOUR_API_TOKEN };
		url = 'https://' + YOUR_ENV_ID + '.live.ruxit.com/api/v1/timeseries/';
		data = {
			'relativeTime' : '5mins',
			'timeseriesId' : conf['timeseriesId'],
			'aggregationType' : conf['aggregation'],
			'entities' : conf['entities']
		};
		r = requests.post(url, json=data, headers=headers);
		if r.status_code == 200:
			j = r.json();
			for entity in conf['entities']:
				for dp in j['result']['dataPoints'][entity]:
					val = "";
					print(datetime.datetime.utcfromtimestamp(int(dp[0]/1000)).isoformat());
					if str(dp[1]) != 'None': 
						val = str(dp[1]);
						cmd = 'aws cloudwatch put-metric-data --metric-name "' + j['result']['entities'][entity] + ' (' + conf['timeseriesId'] + ')" --namespace "Dynatrace" --value ' + val + ' --timestamp ' + datetime.datetime.utcfromtimestamp(int(dp[0]/1000)).isoformat();
						subprocess.call(shlex.split(cmd));
		elif r.status_code == 401:
			print('Dynatrace authentication failed, please check your API token!');
		elif r.status_code == 400:
			print('Wrong timeseriesid, aggregation type or entity combination, please check Dynatrace API help for valid combinations!');
		else:
			print('Error ' + r);
scheduler.enter(1, 1, export_metric, ('first',))
scheduler.run()
