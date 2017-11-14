import os
import shutil

from django.conf import settings
from django.test import override_settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from tprs.models import Project
from . import new_project as script


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test-media'))
class ClientTests(StaticLiveServerTestCase):

    def setUp(self):
        shutil.copytree(
            os.path.join(settings.BASE_DIR, 'testdata'),
            os.path.join(settings.MEDIA_ROOT, 'testdata'))

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_run(self):

        PROJ_NAME = 'new-project'

        testdata_dir = os.path.join(settings.BASE_DIR, 'testdata')

        self.assertEqual(Project.objects.filter(name=PROJ_NAME).count(), 0)

        self.assertEquals(0, script.main([
            'new_project.py',
            '--project-name', PROJ_NAME,
            '--top', os.path.join(testdata_dir, 'plcg_sh2_wt.top'),
            '--mdp', os.path.join(testdata_dir, 'plcg_sh2_wt.mdp'),
            '--gro', os.path.join(testdata_dir, 'plcg_sh2_wt.gro'),
            '--gromppery', self.live_server_url]))

        self.assertEqual(Project.objects.filter(name=PROJ_NAME).count(), 1)

        proj = Project.objects.get(name=PROJ_NAME)

        for filetype in ['top', 'mdp', 'gro']:
            self.assertEqual(
                os.path.basename(getattr(proj, filetype).name),
                '.'.join([PROJ_NAME, filetype]))
