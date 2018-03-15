import tempfile
import os
import logging
import subprocess
import io

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile

from . import util

logger = logging.getLogger(__name__)


class Project(models.Model):

    class Meta:
        ordering = ('name',)

    name = models.CharField(max_length=200, primary_key=True)
    top = models.FileField(upload_to='projects/top')
    mdp = models.FileField(upload_to='projects/mdp')
    gro = models.FileField(upload_to='projects/gro')

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def grompp(self):

        with tempfile.NamedTemporaryFile(suffix=".tpr") as tmp:

            mdout = tempfile.NamedTemporaryFile(suffix=".mdp")
            os.remove(tmp.name)

            grompp = [
                'gmx', 'grompp',
                '-f', self.mdp.path,
                '-c', self.gro.path,
                '-p', self.top.path,
                '-o', tmp.name,
                '-maxwarn', '1',
                '-po', mdout.name
                ]

            logger.debug('Running: %s' % " ".join(grompp))

            p = subprocess.run(
                grompp, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if p.returncode != 0:
                logger.error(
                    'Grompp Failed: %s' % p.stderr.decode("utf-8", "strict"))
                raise Exception(
                    "grompp failed with return code %s" % p.returncode)

            with open(tmp.name, 'rb') as f:
                tpr = io.BytesIO(f.read())

        return tpr


class Submission(models.Model):

    class Meta:
        ordering = ('created', )

    xtc = models.FileField(upload_to='submissions')
    edr = models.FileField(upload_to='submissions')
    tpr = models.FileField(upload_to='submissions')
    gro = models.FileField(upload_to='submissions')
    log = models.FileField(upload_to='submissions')
    cpt = models.FileField(upload_to='submissions')

    project = models.ForeignKey(Project)
    created = models.DateTimeField(auto_now_add=True)

    hostname = models.CharField(
        max_length=200,
        help_text='Name of the host that completed this WU')

    def __str__(self):
        return " ".join([self.project.name, "submission", str(self.index())])

    def index(self):
        """Return the index of this submission, where the ith submission
        for a given project has index i.
        """
        return Submission.objects.filter(
            project=self.project,
            created__lt=self.created).count()

    def align(self, group, tpr_subset):

        tpr_data = util.subset_tpr(self.project.grompp().read(), tpr_subset)
        xtc_data = util.align(self.xtc.path, tpr_data, group)

        prev_aln = Alignment.objects.filter(
            submission__project__name=self.project.name,
            group=group).first()

        aln = Alignment.objects.create(submission=self, group=group,
                                       tpr_subset=tpr_subset)

        logger.debug(
            "Making new aln %s using submission %s.",
            aln, self)

        # Build the xtc file
        fname = '{p}-{i:03d}.xtc'.format(p=self.project.name, i=self.index())
        aln.xtc.save(
            os.path.join(settings.MEDIA_ROOT, 'alignments', self.project.name,
                         fname),
            ContentFile(xtc_data),
            save=True)

        if prev_aln:
            logger.debug('For aln %s, setting group_pdb with old aln %s',
                         aln, prev_aln)
            if prev_aln.group_pdb.name:
                aln.group_pdb = prev_aln.group_pdb
                aln.save()
        else:
            logger.debug('For aln %s, making new group_pdb', aln)

            # group is 'System' because the TPR is already subsetted to
            # have the appropriate set of atoms
            group_pdb = util.make_pdb(xtc_data, tpr_data, group=group)

            fname = '{p}-{g}.pdb'.format(
                p=self.project.name, g=tpr_subset.lower())
            aln.group_pdb.save(
                os.path.join(settings.MEDIA_ROOT, 'alignments',
                             self.project.name, fname),
                ContentFile(group_pdb))


class Alignment(models.Model):

    class Meta:
        ordering = ('created',)

    group_pdb = models.FileField(
        upload_to='alignments', max_length=500,
        help_text="The pdb file representing the masses extracted "
                  "during alignment.")
    xtc = models.FileField(
        upload_to='alignments', max_length=500,
        blank=False, null=False)

    group = models.CharField(
        max_length=50,
        help_text="The gmx group used to align this alignment")
    tpr_subset = models.CharField(
        max_length=50,
        help_text="Atom subset in the TPR extracted to match XTC atom counts.")

    submission = models.OneToOneField(Submission)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Alignment of %s" % self.submission
