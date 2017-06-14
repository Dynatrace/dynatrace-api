# Example implements a stateless SNMP query routine that allows you to monitor a list of metrics
# from a SNMP enabled IBM Data Power network device and send the result over to your Dynatrace 
# environment. 
# As this script is completely stateless it can be installed as a cron job that runs every minute.
# Simple failover can be achieved by running this script on multiple hosts as minute cron jobs.

# IBM DataPower references below
# http://www.middlewareprimer.com/blog/2016/01/01/ibm-websphere-datapower-mib-and-oid-information/
# https://developer.ibm.com/datapower/docker/

from pysnmp.hlapi import *
import requests, time, sched, random

# ---------------------------------------------------------------------------------------------
# Configuration section
# ---------------------------------------------------------------------------------------------
# Configure your Dynatrace environment and API token
YOUR_DT_API_URL = 'https://<YOUR_ENV>.live.dynatrace.com';
YOUR_DT_API_TOKEN = '<YOUR_TOKEN>';

# Configure your SNMP endpoint
YOUR_SNMP_URL = "localhost";
YOUR_SNMP_PORT = 161;

# Configure the global properties of your network device
# DEVICE_ID has to be unique for a specific appliance, if
# you plan to monitor two IBM Data Power appliances you will
# have to start this script twice with different DEVICE_ID
DEVICE_ID = "datapower.one";
DEVICE_NAME = "Data Power One";
DEVICE_TYPE = "IBMDataPower";
DEVICE_IP_ADRESSES = ["172.16.115.211"];
DEVICE_LISTEN_PORTS = ["9999"];
DEVICE_CONFIG_CONSOLE_URL = "";
DEVICE_ICON = "http://assets.dynatrace.com/global/icons/infographic_rack.png";

# Use this configuration section to define which MIB OIDs report as  
# string properties on your IBM Data Power.
props  = [{"properyName" : "Firmware version serial", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.321.1.0'))]},
{"properyName" : "Model type", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.321.2.0'))]}
]
			  
# Use this configuration section to define which scalar metrics are monitored
# for this IBM Data Power 
metrics = [{ "tsId" : "custom:ibm.datapower.tcp.summary.established", "displayName" : "Total TCP cons established", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.1'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.synsent", "displayName" : "Total TCP cons waiting", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.2'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.synreceived", "displayName" : "Total TCP cons received", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.3'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.finwait1", "displayName" : "Total TCP cons fin-wait 1", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.4'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.finwait2", "displayName" : "Total TCP cons fin-wait 2", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.5'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.timewait", "displayName" : "Total TCP cons time wait", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.6'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.closed", "displayName" : "Total TCP cons closed", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.7'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.closedwait", "displayName" : "Total TCP cons closed wait", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.8'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.lastack", "displayName" : "Total TCP cons last-ack", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.9'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.listen", "displayName" : "Total TCP cons listen", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.10'))]},
{ "tsId" : "custom:ibm.datapower.tcp.summary.closing", "displayName" : "Total TCP cons closing", "unit" : "Count", "OID" : [ObjectType(ObjectIdentity('SNMPv2-SMI', 'enterprises', '14685.3.1.12.11'))]}
]
			  	

# ---------------------------------------------------------------------------------------------
# End configuration section
# ---------------------------------------------------------------------------------------------

iter = getCmd(SnmpEngine(),
           CommunityData('public', mpModel=0),
           UdpTransportTarget((YOUR_SNMP_URL, YOUR_SNMP_PORT)),
           ContextData());
		   
next(iter);
# for each object in the properties list
propDict = {};
for i, obj in enumerate(props):
	try:
		# send the query
		errorIndication, errorStatus, errorIndex, varBinds = iter.send(obj["OID"])
		if errorIndication:
			#error
			print( errorIndication )
		elif errorStatus:
			#error
			print( '%s at %s' % (
				errorStatus.prettyPrint(),
				errorIndex and varBinds[int(errorIndex)-1][0] or '?'
				)
			)
		else:
			#success, emit the value to the log
			for oid, value in varBinds:
				propDict[obj["properyName"]] = value.prettyPrint();
	except Exception as e:
		print( 'An unexpected error occurred: %s.' % (e))
		
# Start to fetch the scalar metric values
seriesData = [];
for i, metric in enumerate(metrics):
	try:
		# send the query
		errorIndication, errorStatus, errorIndex, varBinds = iter.send(metric["OID"])
		if errorIndication:
			#error
			print( errorIndication )
		elif errorStatus:
			#error
			print( '%s at %s' % (
				errorStatus.prettyPrint(),
				errorIndex and varBinds[int(errorIndex)-1][0] or '?'
				)
			)
		else:
			#success, emit the value to the Dynatrace series data
			for oid, value in varBinds:
				seriesData.append({ "timeseriesId" : metric["tsId"], "dimensions" : {}, "dataPoints" : [ [ int(time.time() * 1000)  , int(value.prettyPrint()) ] ]});
	except Exception as e:
		print(metric);
		print(value);
		print( 'An unexpected error occurred: %s.'% (e))

#print(seriesData);
		
# Register all the new types of metrics. If metric was already registered before the call will return 
for tsDef in metrics:
	print("Register metric: " + tsDef["displayName"]);
	tsdef = { "displayName" : tsDef["displayName"], "unit" : tsDef["unit"], "dimensions": [], "types": [ DEVICE_TYPE ] };
	r = requests.put(YOUR_DT_API_URL + '/api/v1/timeseries/' + tsDef["tsId"] +'?Api-Token=' + YOUR_DT_API_TOKEN, json=tsdef);
	print(r);

print("Send device info");
payload = {
	"displayName" : DEVICE_NAME,  
     "ipAddresses" : DEVICE_IP_ADRESSES,
     "listenPorts" : DEVICE_LISTEN_PORTS,
     "type" : DEVICE_TYPE,
	 "favicon" : DEVICE_ICON,
	 "configUrl" : DEVICE_CONFIG_CONSOLE_URL,
	 "tags": [],
     "properties" : propDict,
     "series" : seriesData
};
	
#print(payload);	
r = requests.post(YOUR_DT_API_URL + '/api/v1/entity/infrastructure/custom/' + DEVICE_ID + '?Api-Token=' + YOUR_DT_API_TOKEN, json=payload);
print(r);