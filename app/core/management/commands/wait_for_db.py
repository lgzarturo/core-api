import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command, detiene la ejecución hasta que este disponible"""

    def handle(self, *args, **options):
        self.stdout.write('Esperando a la base de datos...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write("DB OFF - Esperando 1 segundo más...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('DB ON'))
