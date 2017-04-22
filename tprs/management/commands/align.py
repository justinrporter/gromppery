from django.core.management.base import BaseCommand

from tprs.models import Submission


class Command(BaseCommand):
    help = 'Creates Alignments for Submissions without them.'

    def add_arguments(self, parser):
        parser.add_argument('group', default="Prot-Masses")

    def handle(self, *args, **options):

        self.stdout.write("Aligning all projects to group name " +
                          options['group'])
        subs = Submission.objects.filter(alignment__isnull=True)
        self.stdout.write("Found " + str(subs.count()) +
                          " submissions to align.")

        for sub in subs:
            self.stdout.write("Aligning " + str(sub))
            sub.align(options['group'])
