import io
import os
import shutil

from django.urls import reverse
from django.conf import settings
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from .seralizers import valid_xtc
from .models import Project, Submission


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test-media'))
class SubmissionViewTests(APITestCase):

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

        self.good_data = {
            'hostname': 'debug01',
            'xtc': open(self.filepath('plcg_sh2_wt.xtc'), 'rb'),
            'log': open(self.filepath('plcg_sh2_wt.log'), 'rb'),
            'edr': open(self.filepath('plcg_sh2_wt.edr'), 'rb'),
            'gro': open(self.filepath('plcg_sh2_wt.gro'), 'rb'),
            'cpt': open(self.filepath('plcg_sh2_wt.cpt'), 'rb'),
            'tpr': open(os.path.join(settings.MEDIA_ROOT,
                                     'testdata/plcg_sh2_wt.tpr'), 'rb'),
        }

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def filepath(self, fname):
        return os.path.join(settings.MEDIA_ROOT,
                            'testdata/submission/', fname)

    def test_submit_project(self):

        url = reverse('project-submit', args=('plcg_sh2_wt',))
        response = self.client.post(url, self.good_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 1)

        submission = Submission.objects.first()

        self.assertEqual(submission.project.pk, 'plcg_sh2_wt')
        self.assertEqual(submission.hostname, self.good_data['hostname'])

    def test_submit_bogus_tpr(self):

        self.good_data['tpr'] = io.BytesIO(
            open("/dev/urandom", "rb").read(1000))

        url = reverse('project-submit', args=('plcg_sh2_wt',))
        response = self.client.post(url, self.good_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_bogus_xtc(self):

        self.good_data['xtc'] = io.BytesIO(
            open("/dev/urandom", "rb").read(1000))

        url = reverse('project-submit', args=('plcg_sh2_wt',))
        response = self.client.post(url, self.good_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_bogus_gro(self):

        self.good_data['gro'] = io.BytesIO(
            open("/dev/urandom", "rb").read(1000))

        url = reverse('project-submit', args=('plcg_sh2_wt',))
        response = self.client.post(url, self.good_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_submit_bogus_cpt(self):

        self.good_data['cpt'] = io.BytesIO(
            open("/dev/urandom", "rb").read(1000))

        url = reverse('project-submit', args=('plcg_sh2_wt',))
        response = self.client.post(url, self.good_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(GROMACS_TIMEOUT=1)
    def test_unmatched_xtc(self):

        self.good_data['xtc'] = open('testdata/alanine.xtc', 'rb')

        url = reverse('project-submit', args=('plcg_sh2_wt',))
        response = self.client.post(url, self.good_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
