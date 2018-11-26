from django.contrib import admin

from .models import Project, Submission, Alignment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'n_submissions', 'created', 'mdp', 'top', 'gro')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'project', 'index', 'created', 'alignment')
    list_filter = ('hostname',
                   'project__name',
                   ('alignment', admin.BooleanFieldListFilter),)


@admin.register(Alignment)
class AlignmentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'project', 'tpr_subset', 'group',
                    'created', 'group_pdb')
    list_filter = ('submission__project__name',)
