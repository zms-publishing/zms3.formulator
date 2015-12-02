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

%s

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
	
	// Handle type=='mailattachment' 
	// by storing filename at hidden field to keep it for storing/sending
	// and check filesize by custom validator - see lines 171 + 202
	$("div[data-schemapath$='FILEDATA']").find("input[type='file']").change(function() {
	    var filename = $(this).val();
	    var lastIndex = filename.lastIndexOf("\\");
	    if (lastIndex >= 0) {
	        filename = filename.substring(lastIndex + 1);
	    }
	    filenamefield = $("div[data-schemapath$='FILENAME']").attr('data-schemapath');
	    ZMSFormulator.getEditor(filenamefield).setValue(filename);
	});
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
		
		// Disable form and show spinner while processing transfer
		// re-enable in case of an error below
		ZMSFormulator.disable();
		document.getElementById('submit').disabled = true;
		document.getElementById('restore').disabled = true;
		document.getElementById('valid_indicator').innerHTML = '<img src="/misc_/zms/loading.gif" alt="Transferring..."/>';
		
		$.ajax({
			type : 'POST',
			url : '%s/putData',
			data : data,
			dataType : 'json'
		})
		.always(function(res) {
			var text = res.responseText;
			if (text == 'OK') {
				document.getElementById('valid_indicator').style.color = 'green';
				document.getElementById('valid_indicator').textContent = JSONEditor.defaults.translate('hint_datasent');
				$('#ZMSFormulatorFeedback').modal('show');
			}
			else if (text == 'NOK') {
				ZMSFormulator.enable();
				document.getElementById('submit').disabled = false;
				document.getElementById('restore').disabled = false;
				document.getElementById('valid_indicator').style.color = 'red';				
				document.getElementById('valid_indicator').textContent = JSONEditor.defaults.translate('hint_datanotsent');			
			}
			else {
				ZMSFormulator.enable();
				document.getElementById('submit').disabled = false;
				document.getElementById('restore').disabled = false;
				document.getElementById('valid_indicator').style.color = 'red';				
				document.getElementById('valid_indicator').textContent = JSONEditor.defaults.translate('hint_erroroccured');
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
        message: JSONEditor.defaults.translate('hint_emailsyntax')
      });
    }
  }
  if(schema.format==="mailattachment") {
	bytes = Math.floor((value.length-value.split(',')[0].length-1)/1.33333);
	if(bytes > 3*1024*1024) {
	  // Errors must be an object with `path`, `property`, and `message`
	  errors.push({
	    path: path,
	    property: 'format',
	    message: 'hint_emailtoolarge'
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
		indicator.textContent = JSONEditor.defaults.translate('hint_checkinput');
		if (errors[0].message=='hint_emailtoolarge') {
			errordiv = $("div[data-schemapath$='"+errors[0].path+"']").find("p[class^='help-block']");
			errordiv.parent().addClass('has-error');
			errormsg = errordiv.html();
			if (errormsg.lastIndexOf("Max.")<0) {
				errordiv.html(errormsg + ' <strong style="color:red;">Max. 3MB!</strong>');
			}
		}
	}
	// Valid
	else {
		submit.disabled = false;
		indicator.style.color = 'green';
		indicator.textContent = '';
		$("div[class$='has-error']").removeClass('has-error');
	}
	// Translate
	$("p[class^='help-block'] strong").each(function() {
		if ($(this).text()==='Type:') {
			$(this).text(JSONEditor.defaults.translate('hint_filetype'));
		}
		else if ($(this).text()==='Size:') {
			$(this).text(JSONEditor.defaults.translate('hint_filesize'));
		}
	});
	
	%s
});