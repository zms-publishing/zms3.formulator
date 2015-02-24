// zms3.formulator.JSONEditor.js

// Initialize the ZMSFormulator
var ZMSFormulator = new JSONEditor(document.getElementById('editor_holder'), {
	
	// Enable fetching schemas via ajax
	ajax : true,

	// The schema for the ZMSFormulator
	schema : {
		"$ref" : "%s/getJSONSchema"
	},

	disable_collapse : true,
	disable_edit_json : true,
	disable_properties : true,
	theme : 'bootstrap3'
});

var onloadCallback = function() {
    grecaptcha.render('reCAPTCHA', {
    	'sitekey' : '%s',
    	'theme' : 'light',
    	'callback' : function(response) {
            //console.log(response);
        }
    });
};

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
		data['reCAPTCHA'] = grecaptcha.getResponse();
				
		$.ajax({
			type : 'POST',
			url : '%s/putData',
			data : data,
			dataType : 'json'
		})
		.always(function(res) {
			var text = res.responseText;
			console.log(text);
			document.getElementById('valid_indicator').textContent = text;			
			if (text == 'Data was sent.') {
				document.getElementById('valid_indicator').style.color = 'green';
				ZMSFormulator.disable();
				document.getElementById('submit').disabled = true;
				document.getElementById('restore').disabled = true;
			}
			else {
				document.getElementById('valid_indicator').style.color = 'red';				
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

// Hook up the validation indicator to update its 
// status whenever the ZMSFormulator changes
ZMSFormulator.on('change', function() {
	// Get an array of errors from the validator
	var errors = ZMSFormulator.validate();

	var indicator = document.getElementById('valid_indicator');

	// Not valid
	if (errors.length) {
		indicator.style.color = 'red';
		indicator.textContent = "Form invalid.";
	}
	// Valid
	else {
		//indicator.style.color = 'green';
		//indicator.textContent = "valid";
	}
});