from django.core.management.base import BaseCommand, CommandError

from tprs.models import Submission
from tprs.util import get_tpr_groups

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

        groups = get_tpr_groups(subs[0].project.grompp().read())

        if options['group'] not in groups:
            raise CommandError(
                ('Group "%s" does not exist in tpr for "%s"; availiable '
                 'groups are: %s.') %
                (options['group'], subs[0].project.name, groups))

        for sub in subs:
            self.stdout.write("Aligning " + str(sub))
            sub.align(options['group'])
