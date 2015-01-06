// zms3.formulator.JSONEditor.js

// Initialize the editor
var editor = new JSONEditor(document.getElementById('editor_holder'), {
	
	// Enable fetching schemas via ajax
	ajax : true,

	// The schema for the editor
	schema : {
		"$ref" : "%s/getJSONSchema"
	},

	disable_collapse : true,
	disable_edit_json : true,
	disable_properties : true,
	theme : 'bootstrap3',
	
	// Options [JS]
	%s
});

// Now the api methods will be available
editor.on('ready',function() {
	
	// onReady [JS]
	%s
});

// Hook up the submit button to log to the console
document.getElementById('submit').addEventListener('click', function() {

	var errors = editor.validate();

	if (!errors.length) {

		// Get the value from the editor
		var data = editor.getValue();

		//console.log(data);
		//alert(JSON.stringify(data));
		editor.disable();
		document.getElementById('submit').disabled = true;
		document.getElementById('restore').disabled = true;
		document.getElementById('valid_indicator').style.color = 'green';
		document.getElementById('valid_indicator').textContent = "Data sent.";
		
		$.ajax({
			type : 'POST',
			url : '%s/putData',
			data : data,
			dataType : 'json'
		}).success(function(response) {
			if (response && response.id) {
				/*  success actions */

			} else {
				/* server-side validation error */

			}
		}).error(function() {
			/* ajax error */

		});

	} else {
		/* client-side validation error */

	}
});

// Hook up the Restore to Default button
document.getElementById('restore').addEventListener('click', function() {
	editor.setValue(editor.options.startval);
});

// Hook up the enable/disable button
/*
document.getElementById('enable_disable').addEventListener('click', function() {
	// Enable form
	if (!editor.isEnabled()) {
		editor.enable();
	}
	// Disable form
	else {
		editor.disable();
	}
});
*/

// Hook up the validation indicator to update its 
// status whenever the editor changes
editor.on('change', function() {
	// Get an array of errors from the validator
	var errors = editor.validate();

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