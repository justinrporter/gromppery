import os
import shutil

from django.conf import settings
from django.test import override_settings, TestCase

from .models import Project
from . import util


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test-media'))
class UtilTests(TestCase):

    def setUp(self):
        shutil.copytree(
            os.path.join(settings.BASE_DIR, 'testdata'),
            os.path.join(settings.MEDIA_ROOT, 'testdata'))

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_get_tpr_groups(self):

        proj = Project.objects.create(
            name='plcg_sh2_wt',
            gro='testdata/plcg_sh2_wt.gro',
            mdp='testdata/plcg_sh2_wt.mdp',
            top='testdata/plcg_sh2_wt.top'
            )

        tpr_data = proj.grompp()
        groups = util.get_tpr_groups(tpr_data.read())

        self.assertEqual(
            ('System', 'Protein', 'Protein-H', 'C-alpha', 'Backbone',
             'MainChain', 'SideChain', 'SideChain-H', 'Prot-Masses',
             'non-Protein', 'Water', 'SOL', 'non-Water', 'Ion', 'NA',
             'CL', 'Water_and_ions'),
            groups)

    def test_get_subsetted_tpr_groups(self):

        proj = Project.objects.create(
            name='plcg_sh2_wt',
            gro='testdata/plcg_sh2_wt.gro',
            mdp='testdata/plcg_sh2_wt.mdp',
            top='testdata/plcg_sh2_wt.top'
            )

        tpr_data = proj.grompp()
        subtpr_data = util.subset_tpr(tpr_data.read(), 'Prot-Masses')

        groups = util.get_tpr_groups(subtpr_data)

        self.assertEqual(
            ('System', 'Protein', 'Protein-H', 'C-alpha', 'Backbone',
             'MainChain', 'SideChain', 'SideChain-H'),
            groups)
