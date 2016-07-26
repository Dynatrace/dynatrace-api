/* A simple CSV timeseries report generator for Dynatrace API */
console.log("Converting timeseries into CSV")

var https = require('https');
var fs = require('fs');

var YOUR_API_KEY = ""; // replace with your own API key
var YOUR_ENTITY = ""; // choose a specific monitored entity, such as a host e.g. HOST-B64B6B9CB11E2244
var TSID = ""; // choose the timeseries to export, e.g. com.ruxit.builtin:host.cpu.user
var AGGREGATION = "AVG";
var TIME = "hour"
var ENVIRONMENT = "" // replace with your own environment id

// fetch requested timeseries as JSON encoded payload
function fetchTimeseries(key, entity, tsid, aggr, time, env, rfunc) {

	var options = {
		host: env + '.live.ruxit.com',
		path: '/api/v1/timeseries/?Api-Token=' + key + '&relativeTime=' + time + '&entity=' + entity + '&aggregationType=' + aggr + '&timeseriesId=' + tsid	
	};

	callback = function(response) {
		var str = '';
		response.on('data', function (chunk) {
			str += chunk;
		});

		// all data was received, send the result as JSON array
		response.on('end', function () {
			var result = JSON.parse( str );
			rfunc(result.result.dataPoints[entity]);
		});
	}

	https.request(options, callback).end();
}

// fetch timeseries as JSON, convert into CSV 
// and store result into a local file 
fetchTimeseries(YOUR_API_KEY, YOUR_ENTITY, TSID, AGGREGATION, TIME, ENVIRONMENT, function(result) {
    console.log(result);
	var csv = "sep=;\ntimestamp;" + TSID + "\n";
	result.forEach(function (current, index, initial_array) {
		var d = new Date(current[0]);
		csv += d.toUTCString() + ";" + current[1] + "\n";
	});
	
	fs.writeFile("./" + YOUR_ENTITY + ".csv", csv, function(err) {
		if(err) {
			return console.log(err);
		}
	});   
});





