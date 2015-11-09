/*

The MIT License (MIT)

Copyright (c) 2013 Jeremy Dorn, https://github.com/jdorn/json-editor

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

*/

// Initialize the ZMSFormulator
var ZMSFormulator = new JSONEditor(document.getElementById('editor_holder'), {
	
	// Enable fetching schemas via ajax
	ajax : true,

	// The schema for the ZMSFormulator
	schema : {
		"$ref" : "%s/getJSONSchema?lang=%s"
	},

	disable_collapse : true,
	disable_edit_json : true,
	disable_properties : true,
	theme : 'bootstrap3'
});


var GoogleAPISitekey = '%s';
if (GoogleAPISitekey != 'no_site_key') {
	var onloadCallback = function() {
	    grecaptcha.render('reCAPTCHA', {
	    	'sitekey' : GoogleAPISitekey,
	    	'theme' : 'light',
	    	'callback' : function(response) {
	            //console.log(response);
	        }
	    });
	};
}

// Options (JS)
%s

// onReady (JS)
ZMSFormulator.on('ready',function() {
	%s
});

// Hook up the submit button to log to the console
document.getElementById('submit').addEventListener('click', function() {

	var errors = ZMSFormulator.validate();

	if (!errors.length) {

		// Get the value from the ZMSFormulator
		var data = ZMSFormulator.getValue();
		
		// Add the response value from the reCAPTCHA service by Google
		// for server-side verification
		if (GoogleAPISitekey != 'no_site_key') {
			data['reCAPTCHA'] = grecaptcha.getResponse();
		}
				
		$.ajax({
			type : 'POST',
			url : '%s/putData',
			data : data,
			dataType : 'json'
		})
		.always(function(res) {
			var text = res.responseText;
			if (text == 'Data was sent.') {
				document.getElementById('valid_indicator').style.color = 'green';
				ZMSFormulator.disable();
				document.getElementById('submit').disabled = true;
				document.getElementById('restore').disabled = true;
				document.getElementById('valid_indicator').textContent = 'Data was sent.';
				$('#ZMSFormulatorFeedback').modal('show');
			}
			else if (text == 'Data was not sent. Are you a robot?') {
				document.getElementById('valid_indicator').style.color = 'red';				
				document.getElementById('valid_indicator').textContent = 'Data was not sent. Are you a robot?';				
			}
			else {
				document.getElementById('valid_indicator').style.color = 'red';				
				document.getElementById('valid_indicator').textContent = 'An Error occured.';
				console.log(text);
			}
		});	
	}
	else {

	}
});

// Hook up the Restore to Default button
document.getElementById('restore').addEventListener('click', function() {
	ZMSFormulator.setValue(ZMSFormulator.options.startval);
});

// Hook up the enable/disable button
/*
document.getElementById('enable_disable').addEventListener('click', function() {
	// Enable form
	if (!ZMSFormulator.isEnabled()) {
		ZMSFormulator.enable();
	}
	// Disable form
	else {
		ZMSFormulator.disable();
	}
});
*/

// Custom validators must return an array of errors or an empty array if valid
JSONEditor.defaults.custom_validators.push(function(schema, value, path) {
  var errors = [];
  if(schema.format==="email") {
    if(!/^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/.test(value)) {
      // Errors must be an object with `path`, `property`, and `message`
      errors.push({
        path: path,
        property: 'format',
        message: 'E-Mails expect a format like "user@domain.tld"'
      });
    }
  }
  return errors;
});

// Hook up the validation indicator to update its 
// status whenever the ZMSFormulator changes
ZMSFormulator.on('change', function() {
	// Get an array of errors from the validator
	var errors = ZMSFormulator.validate();
	 
	var indicator = document.getElementById('valid_indicator');
	var submit = document.getElementById('submit');

	// Not valid
	if (errors.length) {
		submit.disabled = true;
		indicator.style.color = 'red';
		indicator.textContent = "Please check your input!";
	}
	// Valid
	else {
		submit.disabled = false;
		indicator.style.color = 'green';
		indicator.textContent = "";
	}
	
	%s
});