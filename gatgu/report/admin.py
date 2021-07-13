from django.contrib import admin
from report.models import Report, ReportComment


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Report._meta.fields]

@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ReportComment._meta.fields]