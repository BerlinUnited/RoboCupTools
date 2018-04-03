function loadJson(json, callback) {
	var opts = {
		  lines: 13 // The number of lines to draw
		, length: 28 // The length of each line
		, width: 14 // The line thickness
		, radius: 42 // The radius of the inner circle
		, scale: 1 // Scales overall size of the spinner
		, corners: 1 // Corner roundness (0..1)
		, color: '#000' // #rgb or #rrggbb or array of colors
		, opacity: 0.25 // Opacity of the lines
		, rotate: 0 // The rotation offset
		, direction: 1 // 1: clockwise, -1: counterclockwise
		, speed: 1 // Rounds per second
		, trail: 60 // Afterglow percentage
		, fps: 20 // Frames per second when using setTimeout() as a fallback for CSS
		, zIndex: 2e9 // The z-index (defaults to 2000000000)
		, className: 'spinner' // The CSS class to assign to the spinner
		, top: '50%' // Top position relative to parent
		, left: '50%' // Left position relative to parent
		, shadow: true // Whether to render a shadow
		, hwaccel: false // Whether to use hardware acceleration
		, position: 'fixed' // Element positioning
	};

	var spinner = new Spinner(opts).spin(document.getElementsByTagName("body")[0]);

	d3.request(json)
      	.mimeType("application/json")
    	.response(function(xhr) { return eval(xhr.responseText); })
        .get(function(messages) {
        	spinner.stop();
        	callback(messages);
        });
}

function msToTime(s) {
  // Pad to 2 or 3 digits, default is 2
  var pad = (n, z = 2) => ('00' + n).slice(-z);
  return pad(s/3.6e6|0) + ':' + pad((s%3.6e6)/6e4 | 0) + ':' + pad((s%6e4)/1000|0) + '.' + pad(s%1000, 3);
}

class Config {
	constructor(){
		var _config = {};
		window.location.search.substr(1).split("&").map(function(param){
			var key_value = param.split("=");
			_config[key_value[0]] = decodeURIComponent(key_value[1]);
		});
		this._c = _config;
	}

	get(key) {
		return this._c[key];
	}

	get(key, def) {
		return this._c[key] || def;
	}
}