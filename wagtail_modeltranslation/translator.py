from modeltranslation.translator import TranslationOptions


class WagtailTranslationOptions(TranslationOptions):
    def __init__(self, model):
        super(WagtailTranslationOptions, self).__init__(model)

        # TODO: validate condition
        from wagtail.wagtailcore.models import Page
        if Page in model.__bases__:
            page_fields = (
                'title',
                'slug',
                'seo_title',
                'search_description',
                'url_path',)

            for field in page_fields:
                self.local_fields[field] = set()
                self.fields[field] = set()
