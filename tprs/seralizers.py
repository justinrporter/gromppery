import subprocess
import tempfile

from django.conf import settings

from rest_framework import serializers

from . import models


def valid_xtc(tmpfile):
    return valid_gmx_check(tmpfile, '.xtc')


def valid_gro(tmpfile):
    return valid_gmx_check(tmpfile, '.gro')


def valid_cpt(tmpfile):
    return valid_gmx_check(tmpfile, '.cpt')


def valid_gmx_check(tmpfile, suffix):

    with tempfile.NamedTemporaryFile(suffix=suffix) as f:
        [f.write(c) for c in tmpfile.chunks()]
        f.flush()

        p = subprocess.run(
            ['gmx', 'check', '-f', f.name],
            stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    if p.returncode != 0:
        raise serializers.ValidationError(
            "File didn't pass gmx check." +
            p.stderr.decode('ascii', 'ignore'))


def validate_file_for_tpr(flag, file, tpr, timeout=None):

    if timeout is None:
        timeout = settings.GROMACS_TIMEOUT

    try:
        p = subprocess.run(
            ['gmx', 'check',
             flag, file, '-s1', tpr], timeout=timeout,
            stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    except subprocess.TimeoutExpired:
        raise serializers.ValidationError(
            "Submitted XTC timed out validating with fresh TPR.")

    if p.returncode != 0:
        raise serializers.ValidationError(
            "Submitted XTC failed to validate with fresh TPR: " +
            p.stdout.decode('ascii'))


class ProjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Project
        exclude = []
        read_only_fields = ['created']

    # for some reason DRF doesn't include this field by default even
    # with an empty "exclude"
    name = serializers.CharField(max_length=200)
    submissions = serializers.PrimaryKeyRelatedField(
        source='submission_set', many=True, read_only=True)


class SubmissionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Submission
        exclude = []
        read_only_fields = ['created']

    xtc = serializers.FileField(validators=[valid_xtc])
    gro = serializers.FileField(validators=[valid_gro])
    cpt = serializers.FileField(validators=[valid_cpt])

    def validate(self, data):

        # verify TPRs match
        with tempfile.NamedTemporaryFile(suffix='.tpr') as s1:
            s1.write(data['project'].grompp().read())
            s1.flush()

            with tempfile.NamedTemporaryFile(suffix='.tpr') as s2:
                [s2.write(c) for c in data['tpr'].chunks()]
                s2.flush()

                validate_file_for_tpr('-s2', s2.name, s1.name)

            with tempfile.NamedTemporaryFile(suffix='.xtc') as xtc:
                [xtc.write(c) for c in data['xtc'].chunks()]
                xtc.flush()

                validate_file_for_tpr('-f', xtc.name, s1.name)

        return data
