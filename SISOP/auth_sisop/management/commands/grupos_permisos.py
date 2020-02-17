from django.core.management.base import BaseCommand


class Command(BaseCommand):
    GRUPOS_PERMISOS = {'visualizador'}

    def handle(self, *args, **options):
        pass


