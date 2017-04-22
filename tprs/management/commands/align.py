import multiprocessing

from django.core.management.base import BaseCommand

from tprs.models import Submission


class Command(BaseCommand):
    help = 'Creates Alignments for Submissions without them.'

    def add_arguments(self, parser):
        parser.add_argument('group', default="Prot-Masses")
        parser.add_argument(
            "-j", "--n_jobs", default=multiprocessing.cpu_count(), type=int,
            help="Number of parllel jobs to use.")

    def handle(self, *args, **options):

        subs = Submission.objects.filter(alignment__isnull=True)

        for sub in subs:
            print("Aligning", subs)
            sub.align(options['group'])
