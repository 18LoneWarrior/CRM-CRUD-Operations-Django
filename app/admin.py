from django.contrib import admin
from .models import Record
from import_export.admin import ImportExportModelAdmin

# Register your models here.

# admin.site.register(Record)


@admin.register(Record)
class ViewAdmin(ImportExportModelAdmin):
    pass
