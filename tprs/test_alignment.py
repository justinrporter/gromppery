import os
import shutil

from django.test import TestCase, override_settings
from django.conf import settings
from django.core.management.base import CommandError

from .seralizers import valid_xtc
from .models import Project, Submission, Alignment


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test-media'))
class SubmissionAlignmentTest(TestCase):

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

        self.sub.align('Prot-Masses')

        self.assertEqual(Alignment.objects.count(), 1)
        aln = Alignment.objects.first()

        self.assertEqual(aln.group, 'Prot-Masses')

        self.assertEqual(aln.xtc.path,
                         os.path.join(
                             settings.BASE_DIR, settings.MEDIA_ROOT,
                             'alignments/plcg_sh2_wt/plcg_sh2_wt-000.xtc'))
        try:
            valid_xtc(aln.xtc)
        except:
            self.fail("Aligned xtc didn't validate!")

        self.assertEqual(
            aln.group_pdb.path,
            os.path.join(
                settings.BASE_DIR, settings.MEDIA_ROOT,
                'alignments/plcg_sh2_wt/plcg_sh2_wt-prot-masses.pdb'))
        self.assertTrue(os.path.isfile(aln.group_pdb.path))
        self.assertTrue(len(aln.group_pdb.read()) > 0)

    def test_bogus_align_group(self):

        with self.assertRaises(CommandError):
            self.sub.align('NonExistantGroup')


    def test_align_two(self):

        sub1 = self.sub
        sub2 = Submission.objects.create(
            project=self.project,
            hostname='debug01',
            xtc='testdata/submission/plcg_sh2_wt.xtc',
            log='testdata/submission/plcg_sh2_wt.log',
            edr='testdata/submission/plcg_sh2_wt.edr',
            gro='testdata/submission/plcg_sh2_wt.gro',
            cpt='testdata/submission/plcg_sh2_wt.cpt',
            tpr='testdata/plcg_sh2_wt.tpr')

        sub1.align('Prot-Masses')
        sub2.align('Prot-Masses')

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
