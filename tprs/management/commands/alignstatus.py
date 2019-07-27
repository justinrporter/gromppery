import json
from collections import Counter

from django.core.management.base import BaseCommand

from tprs.models import Submission


class Command(BaseCommand):
    help = 'Checks for submissions without alignments.'

    def handle(self, *args, **options):

        c = Counter([s.project.name for s in
                     Submission.objects.filter(alignment__isnull=True)])

        self.stdout.write("Projects without alignments: " +
                          json.dumps(c, sort_keys=True, indent=4))
