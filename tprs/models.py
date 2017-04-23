import tempfile
import os
import logging
import subprocess
import io

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


class Project(models.Model):

    class Meta:
        ordering = ('created',)

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

    def align(self, group):
        tpr_data = subset_tpr(self.project.grompp().read(), group)
        xtc_data = align(self.xtc.path, tpr_data, 'System')

        aln = Alignment.objects.create(
            submission=self)

        fname = '{p}-{i:03d}.xtc'.format(p=self.project.name, i=self.index())
        aln.xtc.save(
            os.path.join(settings.MEDIA_ROOT, 'alignments', self.project.name,
                         fname),
            ContentFile(xtc_data),
            save=True)


class Alignment(models.Model):

    class Meta:
        ordering = ('created',)

    xtc = models.FileField(upload_to='alignments', blank=False, null=False)
    group = models.CharField(
        max_length=50,
        help_text="The gmx group used to assemble this alignment")

    submission = models.OneToOneField(Submission)
    created = models.DateTimeField(auto_now_add=True)


def subset_tpr(tpr_data, group):

    with tempfile.NamedTemporaryFile(suffix='.tpr') as whole_tpr:
        whole_tpr.write(tpr_data)
        whole_tpr.flush()

        with tempfile.NamedTemporaryFile(suffix='.tpr') as partial_tpr:
            partial_tpr_name = partial_tpr.name

        args = [
            'gmx', 'convert-tpr',
            '-s', whole_tpr.name,
            '-o', partial_tpr_name]

        p = subprocess.Popen(
            args, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        output, _ = p.communicate(group.encode('ascii'))

        if p.returncode != 0:
            print(output.decode('ascii'))
            raise subprocess.CalledProcessError(
                p.returncode, args, output=output)

        try:
            with open(partial_tpr_name, 'rb') as f:
                group_tpr = f.read()
        finally:
            os.remove(partial_tpr_name)

    return group_tpr


def align(xtc_file, tpr_data, group):

    with tempfile.NamedTemporaryFile(suffix='.tpr') as tpr:
        tpr.write(tpr_data)

        with tempfile.NamedTemporaryFile(suffix='.xtc') as xtc_out:
            xtc_out_name = xtc_out.name

        args = [
            'gmx', 'trjconv',
            '-f', xtc_file,
            '-s', tpr.name,
            '-o', xtc_out_name,
            '-pbc', 'whole'
        ]

        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = p.communicate(group.encode('ascii'))

        try:
            with open(xtc_out_name, 'rb') as f:
                xtc_data = f.read()
        except:
            print(out.decode('ascii'))
            raise
        finally:
            os.remove(xtc_out_name)

    return xtc_data
