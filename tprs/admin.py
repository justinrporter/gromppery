from django.contrib import admin

from .models import Project, Submission

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    pass
