import io
import os
import shutil

from django.urls import reverse
from django.conf import settings
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Project, Submission


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'test-media'))
class SubmissionViewTests(APITestCase):

    def setUp(self):
        shutil.copytree(
            os.path.join(settings.BASE_DIR, 'testdata'),
            os.path.join(settings.MEDIA_ROOT, 'testdata'))

        try:
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
        except:
            self.tearDown()
            raise

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)

    def filepath(self, fname):
        return os.path.join(settings.MEDIA_ROOT,
                            'testdata/submission/', fname)

    def test_multiple_project_indexing(self):

        self.project2 = Project.objects.create(
            name='plcg_sh2_wt2',
            gro='testdata/plcg_sh2_wt.gro',
            mdp='testdata/plcg_sh2_wt.mdp',
            top='testdata/plcg_sh2_wt.top')

        subdata = {
            'hostname': 'debug01',
            'xtc': self.filepath('plcg_sh2_wt.xtc'),
            'log': self.filepath('plcg_sh2_wt.log'),
            'edr': self.filepath('plcg_sh2_wt.edr'),
            'gro': self.filepath('plcg_sh2_wt.gro'),
            'cpt': self.filepath('plcg_sh2_wt.cpt'),
            'tpr': os.path.join(settings.MEDIA_ROOT,
                                'testdata/plcg_sh2_wt.tpr'),
        }

        sub1 = Submission.objects.create(project=self.project, **subdata)
        self.assertEqual(sub1.index(), 0)

        sub2 = Submission.objects.create(project=self.project2, **subdata)
        self.assertEqual(sub1.index(), 0)
        self.assertEqual(sub2.index(), 0)

        sub3 = Submission.objects.create(project=self.project, **subdata)

        self.assertEqual(sub1.index(), 0)
        self.assertEqual(sub2.index(), 0)
        self.assertEqual(sub3.index(), 1)

    def test_submit_project(self):

        url = reverse('project-submit', args=('plcg_sh2_wt',))
        response = self.client.post(url, self.good_data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 1)

        submission = Submission.objects.last()

        self.assertEqual(submission.project.pk, 'plcg_sh2_wt')
        self.assertEqual(submission.hostname, self.good_data['hostname'])
        self.assertEqual(submission.index(), 0)

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

        response = self.client.post(url, self.good_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 2)

        submission = Submission.objects.last()
        self.assertEqual(submission.index(), 1)

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

    # This test is disabled at present because I cannot figure out a
    # good way to check this.

    # @override_settings(GROMACS_TIMEOUT=1)
    # def test_unmatched_xtc(self):

    #     self.good_data['xtc'] = open('testdata/alanine.xtc', 'rb')

    #     url = reverse('project-submit', args=('plcg_sh2_wt',))
    #     response = self.client.post(url, self.good_data, format='multipart')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
