from rest_framework import serializers

from . import models


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Project
        exclude = []

    # for some reason DRF doesn't include this field by default even
    # with an empty "exclude"
    name = serializers.CharField(max_length=200)


class SubmissionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Submission
        exclude = ['created']
