from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404

from wsgiref.util import FileWrapper

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response

from . import seralizers
from . import models


@api_view(['GET'])
def tpr(request, protein):

    proj = get_object_or_404(
        models.Project.objects.all(),
        name=protein)

    response = HttpResponse(
        FileWrapper(proj.grompp()),
        content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % protein

    return response


class ProjectViewSet(viewsets.ModelViewSet):
    """API endpoint that allows projects to be viewed or edited.
    """
    queryset = models.Project.objects.all()
    serializer_class = seralizers.ProjectSerializer

    @detail_route(methods=['post'])
    def submit(self, request, pk):

        request.data['project'] = reverse('project-detail', args=(pk,))
        s = seralizers.SubmissionSerializer(data=request.data)

        s.is_valid(raise_exception=True)
        s.save()

        return Response({}, status=status.HTTP_201_CREATED)


class SubmissionViewSet(viewsets.ModelViewSet):
    """API endpoint that allows submissions to be viewed or edited.
    """
    queryset = models.Submission.objects.all()
    serializer_class = seralizers.SubmissionSerializer
