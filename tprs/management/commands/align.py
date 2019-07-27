from django.core.management.base import BaseCommand, CommandError

from tprs.models import Submission
from tprs.util import get_tpr_groups


class Command(BaseCommand):
    help = 'Creates Alignments for Submissions without them.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--group', required=True, type=str,
            help="Align atoms using this group. Also controls output.")

        parser.add_argument(
            '--tpr-subset', required=True, type=str,
            help="Subset tprs using this group. Useful when the atom "
                 "count between TPR and XTC differ.")

        parser.add_argument(
            '--name', required=True, type=str,
            help='The name of the project to make alignments for.')

    def handle(self, *args, **options):

        self.stdout.write("Aligning all projects to group name " +
                          options['group'] +
                          "after subsetting tprs with group %s" %
                          options['tpr_subset'])

        total_proj = Submission.objects.filter(
            project__name=options['name']).count()

        if total_proj == 0:
            raise CommandError("Found 0 projects with name %s" %
                               options['name'])

        subs = Submission.objects.filter(
            alignment__isnull=True, project__name=options['name'])

        if subs.count() == 0:
            raise CommandError(
                "Found no unaligned submissions with name %s (out of %s "
                "total projects)." % (options['name'], total_proj))

        self.stdout.write("Found " + str(subs.count()) +
                          " submissions to align.")

        groups = get_tpr_groups(subs[0].project.grompp().read())
        if options['group'] not in groups:
            raise CommandError(
                ('Group "%s" does not exist in tpr for "%s"; availiable '
                 'groups are: %s.') %
                (options['group'], subs[0].project.name, groups))
        if options['tpr_subset'] not in groups:
            raise CommandError(
                ('Group "%s" does not exist in tpr for "%s"; availiable '
                 'groups are: %s.') %
                (options['tpr_subset'], subs[0].project.name, groups))

        for sub in subs:
            self.stdout.write("Aligning " + str(sub))
            sub.align(
                group=options['group'],
                tpr_subset=options['tpr_subset'])
