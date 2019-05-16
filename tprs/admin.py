from django.contrib import admin

from .models import Project, Submission, Alignment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # date_hierarchy = ('created',)
    list_display = ('__str__', 'n_submissions', 'created', 'mdp', 'top', 'gro')
    search_fields = ('name', 'mdp', 'top', 'gro')
    readonly_fields = ('created',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    # date_hierarchy = ('created',)
    list_display = ('__str__', 'hostname', 'project', 'index',
                    'created', 'alignment')
    list_filter = ('hostname', 'project__name',
                   ('alignment', admin.BooleanFieldListFilter),)
    search_fields = ('project__name', 'hostname', 'project__mdp',
                     'project__top', 'project__gro',)
    readonly_fields = ('created',)


@admin.register(Alignment)
class AlignmentAdmin(admin.ModelAdmin):
    # date_hierarchy = ('created',)
    list_display = ('__str__', 'project', 'tpr_subset', 'group',
                    'created', 'group_pdb')
    list_filter = ('submission__project__name',
                   'submission__hostname')
    lookup_allowed = ('submission__project__name',
                      'submission__hostname')
    search_fields = ('tpr_subset', 'group', 'group_pdb',
                     'submission__project__name',
                     'submission__hostname',
                     'submission__project__mdp',
                     'submission__project__top',
                     'submission__project__gro',)
    readonly_fields = ('tpr_subset', 'group', 'tpr_subset', 'created')
