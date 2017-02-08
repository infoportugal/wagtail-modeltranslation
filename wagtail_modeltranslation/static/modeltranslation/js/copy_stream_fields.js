/* Creates the copy buttons in the header of each stream field */

init_copy_stream_fields = function(){
	//All the stream fields with all his content
	var allStreamFields = $('li.stream-field:not([initialized])');
	allStreamFields.attr("initialized", "1");

	/* Iterate all stream fields, put the copy buttons in each one.*/
	for (var i = 0; i < allStreamFields.length; i++) {
		var is_streamfield_in_inlinepanel = false;
		//Current Field with all content
		var currentStreamField = allStreamFields[i];
		//Current Field header
		var header = $(currentStreamField).children('h2')[0];
		if (!header) { //True if StreamField inside InlinePanel
			is_streamfield_in_inlinepanel = true;
			var header = $(currentStreamField).find('label:first')[0];
		}
		//Search for the input field so that we can get is id to know the field's name.
		var streamFieldDiv = $(currentStreamField).find('div.sequence-container.sequence-type-stream')[0];
		var fieldId = $(streamFieldDiv).children('input')[0].id;
		
		if (is_streamfield_in_inlinepanel) {
			var relatedModel = fieldId.split('-')[0];
			var relatedModelOffset = fieldId.split('-')[1];
			var fieldIdPrefix = fieldId.split('-').slice(0,2).join("-") + "-";
			var fieldInfos = fieldId.split('-').slice(2,3).join("-");
			var fieldIdPostfix = "-" + fieldId.split('-').slice(3).join("-");
		}
		else {
			var relatedModel = '';
			var relatedModelOffset = '';
			var fieldIdPrefix = "";
			var fieldInfos = fieldId.split('-')[0];
			var fieldIdPostfix = "-" + fieldId.split('-').slice(1).join("-");
		}
		
		var lastUnderscore = fieldInfos.lastIndexOf("_");
	    var fieldName = fieldInfos.substring(0, lastUnderscore);
	    var fieldLang = fieldInfos.substring(lastUnderscore + 1, fieldInfos.length);
    
		//The cycle to create the buttons for copy each language field
		var copyContentString = 'Copy content from';
		header.innerHTML += '<div class="translation-field-copy-wrapper">'+copyContentString+': </div>';
		for (var j = 0; j < langs.length; j++) {
			if ($("#" + fieldIdPrefix + fieldName + "_" + langs[j] + fieldIdPostfix).length && fieldLang != langs[j]) {
				var currentFieldID = fieldName + '_' + fieldLang;
				var targetFieldID = fieldName + '_' + langs [j];
				$(header).children('.translation-field-copy-wrapper')[0].innerHTML += '<button class="translation-field-copy" current-lang-code="'+ currentFieldID +'" data-lang-code="'+ targetFieldID +'" related-model="' + relatedModel + '" related-model-offset="' + relatedModelOffset + '">'+langs[j]+'</button>';
			};
		};
	};

	/* on click binding */
	allStreamFields.find('.translation-field-copy').click(function(event){
		event.preventDefault();
		var lang = $(this).attr('data-lang-code');
		var currentLang = $(this).attr('current-lang-code');
		var relatedModel = $(this).attr('related-model');
		var relatedModelOffset = $(this).attr('related-model-offset');
		requestCopyField(lang, currentLang, relatedModel, relatedModelOffset);
	});
	
	/* Initialize new elements inside InlinePanel added by the user */
	allStreamFields.parents("ul.multiple").siblings("p.add").click(function(){
		window.setTimeout(init_copy_stream_fields, 500);
	});
}

$(document).ready(function(){
	init_copy_stream_fields();
});

/* Copy the content of originID field to the targetID field */
function requestCopyField(originID, targetID, relatedModel, relatedModelOffset) {
	/* Get the originID field and convert him to json string */
	var serializedForm = $("#page-edit-form").serializeArray();
	var serializedOriginField = $.grep(serializedForm, function(obj){
		if (relatedModel)
			return obj.name.indexOf(relatedModel + "-" + relatedModelOffset + "-" + originID) >= 0;
		return obj.name.indexOf(originID) >= 0;
	});
	var jsonString = JSON.stringify(serializedOriginField);
	/*
	 * AJAX request that returns the html content of originID field
	 * with the id's changed to targetID
	 */
	$.ajax({
		url: 'copy_translation_content',
		type: 'POST',
		dataType: 'json',
		data: {'origin_field_name': originID, 'target_field_name': targetID, 'related_model': relatedModel, 'related_model_offset': relatedModelOffset, 'serializedOriginField': jsonString},
	})
	.done(function(data) {
		/* Put the html data in the targetID field */
		var target = targetID;
		if (relatedModel)
			target = relatedModel + "-" + relatedModelOffset + "-" + targetID;
		var wrapperDiv = $("#"+target+"-count").parents('.input')[0];
		$(wrapperDiv).html(data);
	})
	.fail(function(error) {
		console.log("wagtail-modeltranslation error: %s", error.responseText);
	})

}
