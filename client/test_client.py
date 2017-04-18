import os
import shutil
import tempfile

from django.conf import settings
from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from tprs.models import Project, Submission
from . import gromppery_client as client


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test-media'))
class ClientTests(StaticLiveServerTestCase):

    def setUp(self):
        shutil.copytree(
            os.path.join(settings.BASE_DIR, 'testdata'),
            os.path.join(settings.MEDIA_ROOT, 'testdata'))

        short_mdp = os.path.join(settings.MEDIA_ROOT, 'testdata', 'short.mdp')
        with open(short_mdp, 'w') as mdp:
            with open('testdata/plcg_sh2_wt.mdp', 'r') as f:
                for line in f.readlines():
                    if 'nsteps' in line.split():
                        mdp.write('nsteps = 500 ; .01 ns')
                    elif 'nstxtcout' in line.split():
                        mdp.write('nstxtcout = 25   ; 10 ps')
                    elif 'nstenergy' in line.split():
                        mdp.write('nstenergy = 25   ; 10 ps')
                    else:
                        mdp.write(line)

        self.project = Project.objects.create(
            name='plcg_sh2_wt',
            gro='testdata/plcg_sh2_wt.gro',
            mdp=short_mdp,
            top='testdata/plcg_sh2_wt.top'
            )

        self.scratchpath = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
        shutil.rmtree(self.scratchpath)

    def test_submit(self):

        submission_dir = os.path.join(
            settings.BASE_DIR, 'testdata', 'submission')

        files = {
            'xtc': os.path.join(submission_dir, 'plcg_sh2_wt.xtc'),
            'edr': os.path.join(submission_dir, 'plcg_sh2_wt.edr'),
            'log': os.path.join(submission_dir, 'plcg_sh2_wt.log'),
            'cpt': os.path.join(submission_dir, 'plcg_sh2_wt.cpt'),
            'gro': os.path.join(submission_dir, 'plcg_sh2_wt.gro'),
            'tpr': os.path.join(settings.BASE_DIR, 'testdata',
                                'plcg_sh2_wt.tpr')
        }

        client.submit_work(
            self.live_server_url + '/api',
            tag=self.project.name,
            files=files)

        self.assertEqual(Submission.objects.count(), 1)

        sub = Submission.objects.first()
        for ftype, testfile in files.items():
            self.assertEqual(getattr(sub, ftype).read(),
                             open(testfile, 'rb').read())

    def test_run(self):

        client.main([
            'gromppery_client.py',
            '--protein', self.project.name,
            '--scratch', self.scratchpath,
            '--iterations', '1',
            '--gromppery', self.live_server_url + '/api'])
