import copy

from django.core.management.commands.makemigrations import \
    Command as MakeMigrationsCommand
from django.db.migrations.autodetector import MigrationAutodetector


def autodetector_decorator(func):
    def wrapper(self, from_state, to_state, questioner=None):
        # Replace to_state.app_configs.models and to_state.models' version of page with the old one
        # so no changes are detected by MigrationAutodetector
        from_state_page = from_state.concrete_apps.get_model('wagtailcore', 'page')
        new_to_state = copy.deepcopy(to_state)
        new_to_state.apps.app_configs['wagtailcore'].models['page'] = from_state_page
        new_to_state.models['wagtailcore', 'page'] = from_state.models['wagtailcore', 'page']

        return func(self, from_state, new_to_state, questioner)
    return wrapper


class Command(MakeMigrationsCommand):
    help = "Creates new migration(s) for apps except wagtailcore's Page."

    def handle(self, *args, **options):
        old_autodetector_init = MigrationAutodetector.__init__
        MigrationAutodetector.__init__ = autodetector_decorator(MigrationAutodetector.__init__)

        try:
            super(Command, self).handle(*args, **options)

        finally:
            MigrationAutodetector.__init__ = old_autodetector_init
