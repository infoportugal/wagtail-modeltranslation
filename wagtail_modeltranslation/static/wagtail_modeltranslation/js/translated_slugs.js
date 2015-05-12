$(document).ready(function() {
    $.each(langs, function(idx, lang_code){
        $('#id_title_'+lang_code).on('focus', function() {
            console.log('focus');
            $('#id_slug_'+lang_code).data('previous-val', $('#id_slug_'+lang_code).val());
            $(this).data('previous-val', $(this).val());
        });

        $('#id_title_'+lang_code).on('keyup keydown keypress blur', function() {
            if ($('body').hasClass('create') || (!$('#id_slug_'+lang_code).data('previous-val').length || cleanForSlug($('#id_title_'+lang_code).data('previous-val')) === $('#id_slug_'+lang_code).data('previous-val'))) {
                // only update slug if the page is being created from scratch, if slug is completely blank, or if title and slug prior to typing were identical
                $('#id_slug_'+lang_code).val(cleanForSlug($('#id_title_'+lang_code).val()));
            }
        });
    });
});