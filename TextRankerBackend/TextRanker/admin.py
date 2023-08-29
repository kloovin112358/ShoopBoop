from django.contrib import admin

from .models import *


class BoopReportInline(admin.TabularInline):
    model = BoopReport
    extra = 1


@admin.register(Boop)
class BoopAdmin(admin.ModelAdmin):
    inlines = [
        BoopReportInline,
    ]


admin.site.register(BoopReport)
admin.site.register(UserPOSTSubmissionWarning)
