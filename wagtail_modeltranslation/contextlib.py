from django.utils.translation import activate
from modeltranslation.utils import get_language


class set_language:
    """
    Context manager to safely change language momentarily

    Usage:
        with set_language('en'):
            en_url = obj.get_absolute_url()
    """
    def __init__(self, lang):
        self.language = lang
        self.current_language = get_language()

    def __enter__(self):
        activate(self.language)

    def __exit__(self, exctype, excinst, exctb):
        activate(self.current_language)
