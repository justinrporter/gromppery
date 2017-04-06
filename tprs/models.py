import tempfile
import os
import logging
import subprocess
import io

from django.db import models

logger = logging.getLogger(__name__)


class Project(models.Model):

    class Meta:
        ordering = ('created',)

    name = models.CharField(max_length=200, primary_key=True)
    top = models.FileField()
    mdp = models.FileField()
    gro = models.FileField()

    created = models.DateTimeField(auto_now_add=True)

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
