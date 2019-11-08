/* Creates the copy buttons in the header of each stream field */
$(document).ready(function(){
	//All the stream fields with all his content
	var allStreamFields = $('li.stream-field');

	/* Iterate all stream fields, put the copy buttons in each one.*/
	for (var i = 0; i < allStreamFields.length; i++) {
		//Current Field with all content
		var currentStreamField = allStreamFields[i];
		//Current field header
    var header;
    //Current field name
    var fieldLang = "";
    //Current field language
    var fieldName = "";
    if(versionCompare(WAGTAIL_VERSION,'2.6.0', {zeroExtend: true})===-1){
      // Wagtail < 2.6 
      header = $(currentStreamField).children('h2')[0];
      //Search for the input field so that we can get is id to know the field's name.
      let streamFieldDiv = $(currentStreamField).find('div.sequence-container.sequence-type-stream')[0];
      let fieldInfos = $(streamFieldDiv).find('input')[0].id.split('-')[0];
      let lastUnderscore = fieldInfos.lastIndexOf("_");
      fieldName = fieldInfos.substring(0, lastUnderscore);
      fieldLang = fieldInfos.substring(lastUnderscore + 1, fieldInfos.length);
    } else if(versionCompare(WAGTAIL_VERSION,'2.7.0', {zeroExtend: true})===-1){
      // Wagtail < 2.7 
      header = $(currentStreamField).children('.title-wrapper')[0];
      //Search for the input field so that we can get is id to know the field's name.
      let streamFieldDiv = $(currentStreamField).find('div.sequence-container.sequence-type-stream')[0];
      let fieldInfos = $(streamFieldDiv).find('input')[0].id.split('-')[0];
      let lastUnderscore = fieldInfos.lastIndexOf("_");
      fieldName = fieldInfos.substring(0, lastUnderscore);
      fieldLang = fieldInfos.substring(lastUnderscore + 1, fieldInfos.length);
    } else {
      // Wagtail >= 2.7 
      header = $(currentStreamField).children('.title-wrapper')[0];
      //Search for the input field so that we can get is id to know the field's name.
      let streamFieldDiv = $(currentStreamField).find('.field-content')[0];
      let fieldInfos = $(streamFieldDiv).find('input')[0].id.split('-')[0];
      let lastUnderscore = fieldInfos.lastIndexOf("_");
      fieldName = fieldInfos.substring(0, lastUnderscore);
      fieldLang = fieldInfos.substring(lastUnderscore + 1, fieldInfos.length);
    }
		//The cycle to create the buttons for copy each language field
		header.innerHTML += '<div class="translation-field-copy-wrapper">Copy content from: </div>';
		for (var j = 0; j < langs.length; j++) {
			if (fieldLang != langs[j]) {
				var currentFieldID = fieldName + '_' + fieldLang;
				var targetFieldID = fieldName + '_' + langs [j];
				$(header).children('.translation-field-copy-wrapper')[0].innerHTML += `<button class="button translation-field-copy" current-lang-code="${currentFieldID}" data-lang-code="${targetFieldID}">${langs[j]}</button>`;
			};
		};
	};

	/* on click binding */
	$('.translation-field-copy').click(function(event){
		event.preventDefault();
		var lang = $(this).attr('data-lang-code');
		var currentLang = $(this).attr('current-lang-code');
		requestCopyField(lang, currentLang);
	});
});

/* Copy the content of originID field to the targetID field */
function requestCopyField(originID, targetID) {
	/* Get the originID field and convert him to json string */
	var serializedForm = $("#page-edit-form").serializeArray();
	var serializedOriginField = $.grep(serializedForm, function(obj){return obj.name.indexOf(originID) >= 0;});
	var jsonString = JSON.stringify(serializedOriginField);

	/*
	 * AJAX request that returns the html content of originID field
	 * with the id's changed to targetID
	 */
	$.ajax({
		url: 'copy_translation_content',
		type: 'POST',
		dataType: 'json',
		data: {'origin_field_name': originID, 'target_field_name': targetID, 'serializedOriginField': jsonString},
	})
	.done(function(data) {
		/* Put the html data in the targetID field */
		var wrapperDiv = $(`#${targetID}-count`).parents('.input')[0];
		$(wrapperDiv).html(data);
	})
	.fail(function(error) {
		console.log(`wagtail-modeltranslation error: ${error.responseText}`);
	})

}
