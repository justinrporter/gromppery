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

    def align(self, group):

        tpr_data = subset_tpr(self.project.grompp().read(), group)
        xtc_data = align(self.xtc.path, tpr_data, 'System')

        prev_aln = Alignment.objects.filter(
            submission__project__name=self.project.name,
            group=group).first()

        aln = Alignment.objects.create(submission=self, group=group)

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
            group_pdb = make_pdb(xtc_data, tpr_data, group='System')

            fname = '{p}-{g}.pdb'.format(
                p=self.project.name, g=group.lower())
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
        help_text="The gmx group used to assemble this alignment")

    submission = models.OneToOneField(Submission)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Alignment of %s" % self.submission


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
            '-pbc', 'nojump'
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


def make_pdb(xtc_data, tpr_data, group='System', pbc='nojump'):
    """Build a PDB file without periodic boundary conditions out of an
    XTC and TPR.
    """

    try:
        # write the binary data to files for GMX to read
        tpr = tempfile.NamedTemporaryFile(suffix='.tpr')
        tpr.write(tpr_data)

        xtc = tempfile.NamedTemporaryFile(suffix='.xtc')
        xtc.write(xtc_data)

        # get a temp file name for the output pdb
        pdb_out = tempfile.NamedTemporaryFile(suffix='.pdb')
        pdb_out_name = pdb_out.name
        pdb_out.close()

        args = [
            'gmx', 'trjconv',
            '-f', xtc.name,
            '-s', tpr.name,
            '-o', pdb_out_name,
            '-e', '1',
            '-pbc', pbc
        ]

        p = subprocess.Popen(
            args, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

        out, _ = p.communicate(group.encode('ascii'))
    finally:
        xtc.close()
        tpr.close()

    try:
        with open(pdb_out_name, 'rb') as f:
            pdb_data = f.read()
    except:
        print(out.decode('ascii'))
        raise
    finally:
        if os.path.isfile(pdb_out_name):
            os.remove(pdb_out_name)

    return pdb_data
