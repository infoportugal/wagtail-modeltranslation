$(document).ready(function () {
    /* Only non-live pages should auto-populate the slug from the title */
    if (!$('body').hasClass('page-is-live')) {
        if(!wagtailModelTranslations.translate_slugs) {
            lang_code = wagtailModelTranslations.defaultLanguage.replace("-", "_");
            title_selector = '#id_title_' + lang_code;
            slug_selector = '#id_slug';
            slugAutoPopulateTranslation(title_selector, slug_selector);
        } else {
            $.each(wagtailModelTranslations.languages, function (idx, lang_code) {
                lang_code = lang_code.replace("-", "_");
                title_selector = '#id_title_' + lang_code;
                slug_selector = '#id_slug_' + lang_code;
                slugAutoPopulateTranslation(title_selector, slug_selector);
            });
        }
    }
});

function slugAutoPopulateTranslation(title_selector, slug_selector) {
    var slugFollowsTitle = false;

    $(title_selector).on('focus', function () {
        /* slug should only follow the title field if its value matched the title's value at the time of focus */
        var currentSlug = $(slug_selector).val();
        var slugifiedTitle = cleanForSlug(this.value, true);
        slugFollowsTitle = (currentSlug == slugifiedTitle);
    });

    $(title_selector).on('keyup keydown keypress blur', function () {
        if (slugFollowsTitle) {
            var slugifiedTitle = cleanForSlug(this.value, true);
            $(slug_selector).val(slugifiedTitle);
        }
    });
}
