"""
Example script for monitoring a Raspberry PI
"""
import requests, time, sched, random, os, ssl

YOUR_DT_API_URL = 'https://{id}.live.dynatrace.com';
YOUR_DT_API_TOKEN = '{token}';

tsdef = {
	"displayName" : "CPU temperature",
	"unit" : "Count",
	"dimensions": [
	],
	"types": [
		"Raspberry"
	]
};

r = requests.put(YOUR_DT_API_URL + '/api/v1/timeseries/custom:raspberry.cpu.temperature/?Api-Token=' + YOUR_DT_API_TOKEN, json=tsdef);
print(r);

tsdef2 = {
	"displayName" : "Memory free",
	"unit" : "Count",
	"dimensions": [
	],
	"types": [
		"Raspberry"
	]
};

r = requests.put(YOUR_DT_API_URL + '/api/v1/timeseries/custom:raspberry.memory.free/?Api-Token=' + YOUR_DT_API_TOKEN, json=tsdef2);
print(r);

def getCpuTemperature():
 tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
 cpu_temp = tempFile.read()
 tempFile.close()
 return float(cpu_temp)/1000
 
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

scheduler = sched.scheduler(time.time, time.sleep)

def print_event(name):
	scheduler.enter(60, 1, print_event, ('first',))
	print("Send metric");
	RAM_stats = getRAMinfo();
	payload = {
     "displayName" : "Raspberry",  
     "ipAddresses" : [],
     "listenPorts" : [],
     "type" : "Raspberry",
     "favicon" : "http://assets.dynatrace.com/global/icons/cpu_processor.png",
	 "configUrl" : "",
     "properties" : {
		"manufacturer" : "Dynatrace LLC",
		"schedule" : "60secs",
	 },
     "series" : [
        { "timeseriesId" : "custom:raspberry.cpu.temperature", 
		  "dimensions" : {
		  },
		  "dataPoints" : [ [ int(time.time() * 1000)  , getCpuTemperature() ] ]
		},
		{ "timeseriesId" : "custom:raspberry.memory.free", 
		  "dimensions" : {
		  },
		  "dataPoints" : [ [ int(time.time() * 1000)  , round(int(RAM_stats[2]) / 1000,1) ] ]
		}
	]};
	try:
		r = requests.post(YOUR_DT_API_URL + '/api/v1/entity/infrastructure/custom/raspberry?Api-Token=' + YOUR_DT_API_TOKEN, json=payload);
		print(r);
	except ssl.SSLError:
		print("SSL Error");
print("START")
# Within this example a Python scheduler is used to trigger a metric update every minute.
# To ensure the reliable execution of the script in a real world scenario you could either use a cron job
# or execute the script within a managed execution environment.
scheduler.enter(1, 1, print_event, ('first',))
scheduler.run()