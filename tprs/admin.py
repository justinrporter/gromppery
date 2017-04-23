from django.contrib import admin

from .models import Project, Submission, Alignment

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    pass

@admin.register(Alignment)
class AlignmentAdmin(admin.ModelAdmin):
    pass
