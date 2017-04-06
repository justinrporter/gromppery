from django.http import HttpResponse
from wsgiref.util import FileWrapper

from rest_framework.decorators import api_view
from rest_framework import viewsets

from . import seralizers
from . import models


@api_view(['GET'])
def tpr(request, protein):

    proj = models.Project.objects.get(name=protein)

    response = HttpResponse(
        FileWrapper(proj.grompp()),
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % protein

    return response


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Project.objects.all()
    serializer_class = seralizers.ProjectSerializer
