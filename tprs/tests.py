import tempfile
import subprocess
import os
import shutil

from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Project


def check_tpr(data):

    with tempfile.NamedTemporaryFile(suffix='.tpr') as f:
        f.write(data)
        subprocess.run(['gmx', 'check',
                        '-s1', 'testdata/myh7.tpr',
                        '-s2', f.name],
                       stderr=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL,
                       check=True)


class ProjectTests(APITestCase):

    def test_make_tpr(self):

        proj = Project.objects.create(
            name='myh7',
            gro='testdata/myh7.gro',
            mdp='testdata/myh7.mdp',
            top='testdata/myh7.top'
            )

        tpr = proj.grompp()
        check_tpr(tpr.read())


class ViewTests(APITestCase):

    def setUp(self):
        self.old_mediaroot = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'test-media')

        shutil.copytree(
            os.path.join(self.old_mediaroot, 'testdata'),
            os.path.join(settings.MEDIA_ROOT, 'testdata'))

    def tearDown(self):
        shutil.rmtree(settings.MEDIA_ROOT)
        settings.MEDIA_ROOT = self.old_mediaroot

    def test_tpr_view(self):

        Project.objects.create(
            name='myh7',
            gro='testdata/myh7.gro',
            mdp='testdata/myh7.mdp',
            top='testdata/myh7.top'
            )

        url = reverse('tpr-generate', kwargs={'protein': 'myh7'})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        check_tpr(response.content)

    def test_create_project(self):
        """
        Ensure we can create a new project.
        """

        url = reverse('project-list')

        data = {
            'name': 'myh7',
            'mdp': open('testdata/myh7.mdp', 'rb'),
            'top': open('testdata/myh7.top', 'rb'),
            'gro': open('testdata/myh7.gro', 'rb'),
            }

        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.first().pk, 'myh7')
        self.assertEqual(Project.objects.first().name, 'myh7')

        response = self.client.get(reverse('project-list'))
        self.assertEqual(len(response.data['results']), 1)

        Project.objects.first().delete()
