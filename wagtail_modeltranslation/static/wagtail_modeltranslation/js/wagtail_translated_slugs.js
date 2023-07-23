$(document).ready(function () {
    isLive = $('body').hasClass('page-is-live');
    if (!wagtailModelTranslations.translate_slugs) {
        lang_code = wagtailModelTranslations.defaultLanguage.replace("-", "_");
        title_selector = '#id_title_' + lang_code;
        slug_selector = '#id_slug';
        if (!isLive || (isLive && !$(slug_selector).val())) {
            slugAutoPopulateTranslation(title_selector, slug_selector);
        }
    } else {
        $.each(wagtailModelTranslations.languages, function (idx, lang_code) {
            lang_code = lang_code.replace("-", "_");
            title_selector = '#id_title_' + lang_code;
            slug_selector = '#id_slug_' + lang_code;
            if (!isLive || (isLive && !$(slug_selector).val())) {
                slugAutoPopulateTranslation(title_selector, slug_selector);
            }
        });
    }
});

/**
 * Returns the supplied string as a slug optionally using the vendor URLify util.
 * If not using URLify it will read the global unicodeSlugsEnabled and return a slugified string.
 * 
 * HACK this function has been removed from Wagtail 5+, we restore it temporarily
 *      to allow for slug generation to work as before, but it should be replaced
 *      with the current slug generation system in use by Wagtail
 *
 * @param {string} val - value to be parsed into a slug
 * @param {boolean} useURLify - if true, the vendor URLify will be used
 * @returns {string}
 */
function cleanForSlug(
    val,
    useURLify,
    { unicodeSlugsEnabled = window.unicodeSlugsEnabled } = {}
) {
    if (useURLify) {
        // URLify performs extra processing on the string (e.g. removing stopwords) and is more suitable
        // for creating a slug from the title, rather than sanitising a slug entered manually
        const cleaned = window.URLify(val, 255);

        // if the result is blank (e.g. because the title consisted entirely of stopwords),
        // fall through to the non-URLify method
        if (cleaned) {
            return cleaned;
        }
    }

    // just do the "replace"
    if (unicodeSlugsEnabled) {
        return val
            .replace(/\s+/g, '-')
            .replace(/[&/\\#,+()$~%.'":`@^!*?<>{}]/g, '')
            .toLowerCase();
    }

    return val
        .replace(/\s+/g, '-')
        .replace(/[^A-Za-z0-9\-_]/g, '')
        .toLowerCase();
}

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
