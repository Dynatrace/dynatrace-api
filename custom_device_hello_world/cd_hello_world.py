"""
Example script that shows how to register a custom metric and to send 
custom metric values on a custom network device.
The script also registers a threshold that raises a custom event whenever the threshold is violated.

The script is designed as stateless hello world example that should be called every minute. 
The script reports random values every minute and contains a regular problem pattern that 
is triggered between 11 and 12 every day.
"""
import requests, time, sched, random, datetime

# SaaS
YOUR_DT_API_URL = 'https://YOUR_ENVIRONMENT_ID.live.dynatrace.com'
YOUR_DT_API_TOKEN = 'YOUR_API_TOKEN'

# example data power metric
tsdef = {
	"displayName" : "Total established connections",
	"unit" : "Count",
	"dimensions": [
		"interface"
	],
	"types": [
		"IBMDataPower"
	]
}

r = requests.put(YOUR_DT_API_URL + '/api/v1/timeseries/custom:connections.established?Api-Token=' + YOUR_DT_API_TOKEN, json=tsdef)

# example booking rate metric
bookingRate = {
	"displayName" : "Booking rate",
	"unit" : "PerMinute",
	"dimensions": [
		"airport", "class", "destination"
	],
	"types": [
		"IBMDataPower"
	]
}

r = requests.put(YOUR_DT_API_URL + '/api/v1/timeseries/custom:business.booking.rate?Api-Token=' + YOUR_DT_API_TOKEN, json=bookingRate)

# Define custom event for booking rate drop

event = {
	"timeseriesId": "custom:business.booking.rate",
	"threshold": 50,
	"alertCondition": "BELOW",
	"samples": 5,
	"violatingSamples": 3,
	"dealertingSamples": 2,
	"eventType": "AVAILABILITY_EVENT",
	"eventName": "Flight booking rate drop",
	"description": "The booking rate of {severity} is {alert_condition} the critical threshold of {threshold} in {dimensions}"
}

r = requests.put(YOUR_DT_API_URL + '/api/v1/thresholds/event.business.bookingrate.low?Api-Token=' + YOUR_DT_API_TOKEN, json=event)

def genSeries():
	interfaces = ["interface1", "interface2", "interface3"]
	series = []
	now = datetime.datetime.now()
		
	for interface in interfaces: 
		value = random.randint(450,500)
		if 11 <= now.hour < 12 and interface == "interface1":      
			value = random.randint(0,100)
			print('Data power conection drop pattern active:' + interface)
		series.append({ "timeseriesId" : "custom:connections.established", 
			"dimensions" : { "interface" :interface },
			"dataPoints" : [ [ int(time.time() * 1000)  , value ] ]
		})
		
	# fill booking rate
	airports = ["ATL", "AST", "ATY", "AUN", "AUO", "ANV", "DAA"]
	flclasses = ["first", "business", "coach"]
	destinations = ["domestic", "international"]	
	
	for airport in airports: 
		for flclass in flclasses:
			for destination in destinations:
				rate = random.randint(90,100)
				# ingest a problem pattern
				if 11 <= now.hour < 12 and airport == "AST":
					print('Booking rate drop pattern active:' + airport)
					rate = random.randint(0,10)
				series.append({ "timeseriesId" : "custom:business.booking.rate", 
				  "dimensions" : { "airport" : airport, "class" : flclass, "destination" : destination },
				  "dataPoints" : [ [ int(time.time() * 1000)  , rate ] ]
				})
		
	return series
		

print("Send metric")
payload = {
	"displayName" : "IBM DataPower 1",  
	"ipAddresses" : ["192.168.10.10"],
	"listenPorts" : ["80", "443"],
	"type" : "IBMDataPower",
	"favicon" : "http://assets.dynatrace.com/global/icons/infographic_rack.png",
	"configUrl" : "",
	"series" : genSeries()
}
r = requests.post(YOUR_DT_API_URL + '/api/v1/entity/infrastructure/custom/ibm.datapower.1?Api-Token=' + YOUR_DT_API_TOKEN, json=payload)
print(r)
