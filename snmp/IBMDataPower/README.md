IBMDataPower.py represents a stateless Python script that fetches properties and 
scalar metrics from a configured IBM Data Power network device and sends those
information over to your Dynatrace environment.
Configured as a simple cron job that runs every minute, this script will act as a 
simple monitoring extension to get additional insights into a DataPower and to
attach any SNMP exposed metric into the Dynatrace transactional view.

# Prequisites are
The example uses the PySNMP library that is available here:
http://pysnmp.sourceforge.net/quick-start.html#fetch-snmp-variable

## Install pysnmp
Install pysnmp library by executing following pip command

pip install pysnmp
pip install pysnmp-mibs
