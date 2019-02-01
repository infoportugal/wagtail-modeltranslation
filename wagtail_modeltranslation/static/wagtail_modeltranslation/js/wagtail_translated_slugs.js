$(document).ready(function () {
    /* Only non-live pages should auto-populate the slug from the title */
    if (!$('body').hasClass('page-is-live')) {
        var slugFollowsTitle = false;

        $.each(langs, function (idx, lang_code) {
            lang_code = lang_code.replace("-", "_");
            $('#id_title_' + lang_code).on('focus', function () {
                /* slug should only follow the title field if its value matched the title's value at the time of focus */
                var currentSlug = $('#id_slug_' + lang_code).val();
                var slugifiedTitle = cleanForSlug(this.value, true);
                slugFollowsTitle = (currentSlug == slugifiedTitle);
            });

            $('#id_title_' + lang_code).on('keyup keydown keypress blur', function () {
                if (slugFollowsTitle) {
                    var slugifiedTitle = cleanForSlug(this.value, true);
                    $('#id_slug_' + lang_code).val(slugifiedTitle);
                }
            });
        });
    }
});
