from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from django.db.migrations.autodetector import MigrationAutodetector


# decorate MigrationAutodetector.changes so we can silently remove wagtailcore changes
def changes_decorator(func):
    def wrapper(self, graph, trim_to_apps=None, convert_apps=None, migration_name=None):
        changes = func(self, graph, trim_to_apps, convert_apps, migration_name)
        if 'wagtailcore' in changes:
            del changes['wagtailcore']
        return changes
    return wrapper

MigrationAutodetector.changes = changes_decorator(MigrationAutodetector.changes)


class Command(MakeMigrationsCommand):
    help = "Creates new migration(s) for apps except wagtailcore."
