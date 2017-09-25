from modeltranslation.translator import TranslationOptions


class WagtailTranslationOptions(TranslationOptions):

    @staticmethod
    def any_in(l1, l2):
        return any(i in l1 for i in l2)

    def __init__(self, model):

        from wagtail.wagtailcore.models import Page
        from wagtail.wagtailforms.models import AbstractEmailForm

        if self.any_in([Page, AbstractEmailForm], model.__bases__):
            self.fields += (
                'title',
                'slug',
                'seo_title',
                'search_description',
                'url_path',)

        super(WagtailTranslationOptions, self).__init__(model)
