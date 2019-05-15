//
// Local Node.js service that wraps Dynatrace Data Export API calls for local JavaScript/Browser usage.
//
var express = require('express');
var app = express();
var https = require('https');

app.use(express.static('public'));

var YOUR_API_TOKEN = "<YOUR_TOKEN>";
var YOUR_HOST = "HOST-A3C4D3D278C161FA";

//
// Read the CPU of a given host and return the JSON result
//
app.get('/cpu', function (req, res) {
	var options = {
		host: '<YOUR_ENVIRONMENT>.live.dynatrace.com',
		path: '/api/v1/timeseries/?Api-Token=' + YOUR_API_TOKEN + '&relativeTime=hour&entity=' + YOUR_HOST + '&aggregationType=AVG&timeseriesId=com.dynatrace.builtin:host.cpu.user'	
	};

	callback = function(response) {
		var str = '';
		response.on('data', function (chunk) {
			str += chunk;
		});

		// all data was received, send the result as JSON
		response.on('end', function () {
			res.send(str);
		});
	}

	https.request(options, callback).end();
});

var server = app.listen(8080, function () {
  var host = server.address().address;
  var port = server.address().port;
  console.log('Example app listening at http://%s:%s', host, port);
});
