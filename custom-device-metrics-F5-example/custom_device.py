"""
Example script that shows how to register a custom metric and to send 
custom metric values on a custom network device.
"""
import requests, time, sched, random

YOUR_DT_API_URL = 'https://{id}.live.dynatrace.com';
YOUR_DT_API_TOKEN = '{token}';

tsdef = {
	"displayName" : "Dropped TCP connections",
	"unit" : "Count",
	"dimensions": [
		"nic"
	],
	"types": [
		"F5-Firewall"
	]
};

r = requests.put(YOUR_DT_API_URL + '/api/v1/timeseries/custom:firewall.connections.dropped?Api-Token=' + YOUR_DT_API_TOKEN, json=tsdef);
print(r);

scheduler = sched.scheduler(time.time, time.sleep)
def print_event(name):
	scheduler.enter(60, 1, print_event, ('first',))
	print("Send metric");
	payload = {
     "displayName" : "F5 Firewall 24",  
     "ipAddresses" : ["172.16.115.211"],
     "listenPorts" : ["9999"],
     "type" : "F5-Firewall",
	 "favicon" : "http://assets.dynatrace.com/global/icons/f5.png",
	 "configUrl" : "http://172.16.115.211:8080",
	 "tags": ["user defined tag", "tag2"],
     "properties" : { 
	                 "myProperty" : "anyvalue", "myTestProperty2" : "anyvalue"
                    },
     "series" : [
        { "timeseriesId" : "custom:firewall.connections.dropped", 
		  "dimensions" : { "nic" : "ethernetcard1" },
		  "dataPoints" : [ [ int(time.time() * 1000)  , random.randint(400,500) ] ]
		},
		{ "timeseriesId" : "custom:firewall.connections.dropped", 
		  "dimensions" : { "nic" : "ethernetcard2" },
		  "dataPoints" : [ [ int(time.time() * 1000)  , random.randint(400,500) ] ]
		}
	]
};
	
	r = requests.post(YOUR_DT_API_URL + '/api/v1/entity/infrastructure/custom/f5firewall24?Api-Token=' + YOUR_DT_API_TOKEN, json=payload);
	print(r);

print("START")
scheduler.enter(1, 1, print_event, ('first',))
scheduler.run()



		





