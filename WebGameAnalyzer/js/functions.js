/**/
var spinner = new Spinner({
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
});

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

function loadJson(file) {
	// can only load files via ajax when not local
	if (window.location.protocol !== 'file:') {
		let xhr = new XMLHttpRequest();
		if (xhr) {
			xhr.onloadstart = function(e){ spinner.spin(document.body); };
			xhr.onloadend   = function(e){ spinner.stop(); };
			xhr.onload      = function(e){ document.dispatchEvent(new CustomEvent('newLogFile', { detail: eval(e.target.responseText), })); };
			xhr.open('GET', file);
			xhr.send();
		}
    }
}

function loadFile(file) {
	// make sure we can load files
    if (typeof window.FileReader === 'function') {
		let r = new FileReader();
		r.onloadstart = function(e){ spinner.spin(document.body); };
		r.onloadend   = function(e){ spinner.stop(); };
		r.onload      = function(e){ document.dispatchEvent(new CustomEvent('newLogFile', { detail: eval(e.target.result), })); };
		r.readAsText(file);
	}
}

function addLocalFileSelector(parent) {
	if (typeof window.FileReader === 'function') {
		let pNode = (typeof parent === 'string' || parent instanceof String) ? document.querySelector(parent) : parent;
		let fNode = document.createElement("form");
		fNode.innerHTML = '<fieldset><h2>Select local Json LogFile</h2><input type="file" id="fileinput" accept=".json"></fieldset>';
		fNode.querySelector("#fileinput").onchange = function(e) {

			if (this.files && this.files.length > 0) {
				loadFile(this.files[0]);
			}
		};
		pNode.insertBefore(fNode, pNode.firstChild);
	} else {
		console.log("The file API isn't supported on this browser!");
	}
}

function registerNewLogFileEventHandler(handler) {
	document.addEventListener('newLogFile', function(d){ handler(d.detail); });
}

function msToTime(s) {
	// Pad to 2 or 3 digits, default is 2
	var pad = (n, z = 2) => ('00' + n).slice(-z);
	return pad(s/3.6e6|0) + ':' + pad((s%3.6e6)/6e4 | 0) + ':' + pad((s%6e4)/1000|0) + '.' + pad(s%1000, 3);
}
