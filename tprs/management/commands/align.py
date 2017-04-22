from django.core.management.base import BaseCommand

from tprs.models import Submission


class Command(BaseCommand):
    help = 'Creates Alignments for Submissions without them.'

    def add_arguments(self, parser):
        parser.add_argument('group', default="Prot-Masses")

    def handle(self, *args, **options):

        subs = Submission.objects.filter(alignment__isnull=True)

        for sub in subs:
            print("Aligning", sub)
            sub.align(options['group'])
