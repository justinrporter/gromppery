import os
import shutil
import io

from django.test import TestCase, override_settings
from django.conf import settings
from django.core.management import call_command

from ..seralizers import valid_xtc
from ..models import Project, Submission, Alignment


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test-media'))
class AlignCommandTestCase(TestCase):

    def setUp(self):
        shutil.copytree(
            os.path.join(settings.BASE_DIR, 'testdata'),
            os.path.join(settings.MEDIA_ROOT, 'testdata'))

        self.project = Project.objects.create(
            name='plcg_sh2_wt',
            gro='testdata/plcg_sh2_wt.gro',
            mdp='testdata/plcg_sh2_wt.mdp',
            top='testdata/plcg_sh2_wt.top'
            )

        self.sub = Submission.objects.create(
            project=self.project,
            hostname='debug01',
            xtc='testdata/submission/plcg_sh2_wt.xtc',
            log='testdata/submission/plcg_sh2_wt.log',
            edr='testdata/submission/plcg_sh2_wt.edr',
            gro='testdata/submission/plcg_sh2_wt.gro',
            cpt='testdata/submission/plcg_sh2_wt.cpt',
            tpr='testdata/plcg_sh2_wt.tpr')

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_align(self):

        out = io.StringIO()
        call_command('align', 'Prot-Masses', stdout=out)

        self.assertEqual(Alignment.objects.count(), 1)
        aln = Alignment.objects.first()
        self.assertEqual(aln.xtc.path,
                         os.path.join(
                             settings.BASE_DIR, settings.MEDIA_ROOT,
                             'alignments/plcg_sh2_wt/plcg_sh2_wt-000.xtc'))

        try:
            valid_xtc(aln.xtc)
        except:
            self.fail("Aligned xtc didn't validate!")

    def test_align_two(self):

        self.sub = Submission.objects.create(
            project=self.project,
            hostname='debug02',
            xtc='testdata/submission/plcg_sh2_wt.xtc',
            log='testdata/submission/plcg_sh2_wt.log',
            edr='testdata/submission/plcg_sh2_wt.edr',
            gro='testdata/submission/plcg_sh2_wt.gro',
            cpt='testdata/submission/plcg_sh2_wt.cpt',
            tpr='testdata/plcg_sh2_wt.tpr')

        out = io.StringIO()
        call_command('align', 'Prot-Masses', stdout=out)

        self.assertEqual(Alignment.objects.count(), 2)

        aln0 = Alignment.objects.first()
        self.assertEqual(aln0.xtc.path,
                         os.path.join(
                             settings.BASE_DIR, settings.MEDIA_ROOT,
                             'alignments/plcg_sh2_wt/plcg_sh2_wt-000.xtc'))

        aln1 = Alignment.objects.last()
        self.assertEqual(aln1.xtc.path,
                         os.path.join(
                             settings.BASE_DIR, settings.MEDIA_ROOT,
                             'alignments/plcg_sh2_wt/plcg_sh2_wt-001.xtc'))

        self.assertEqual(
            aln0.group_pdb,
            aln1.group_pdb)
