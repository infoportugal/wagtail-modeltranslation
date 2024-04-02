from django.core.management.commands.migrate import Command as MigrateCommand
from django.db.migrations.autodetector import MigrationAutodetector

from .sync_page_translation_fields import Command as SyncPageTranslationFieldsCommand


# decorate MigrationAutodetector.changes so we can silence any wagtailcore migrations missing warnings
def changes_decorator(func):
    def wrapper(self, graph, trim_to_apps=None, convert_apps=None, migration_name=None):
        changes = func(self, graph, trim_to_apps, convert_apps, migration_name)
        if "wagtailcore" in changes:
            del changes["wagtailcore"]
        return changes

    return wrapper


class Command(MigrateCommand):
    help = (
        "Updates database schema. Manages both apps with migrations and those without. "
        "Updates Wagtail Page translation fields"
    )

    def handle(self, *args, **options):
        old_autodetector_changes = MigrationAutodetector.changes
        MigrationAutodetector.changes = changes_decorator(MigrationAutodetector.changes)

        try:
            super(Command, self).handle(*args, **options)
        finally:
            MigrationAutodetector.changes = old_autodetector_changes

        # Run sync_page_translation_fields command
        sync_page_command = SyncPageTranslationFieldsCommand()
        # Update the dict of sync_page_command with the content of this one
        sync_page_command.__dict__.update(self.__dict__)
        sync_page_command.handle(*args, **options)
