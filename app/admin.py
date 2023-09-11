from django.contrib import admin
from django.contrib.admin import ModelAdmin
import csv
from .models import Record
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django import forms
from .resources import Resource
from tablib import Dataset
from openpyxl import Workbook


# Register your models here.

# admin.site.register(Record)

def export_csv(modeladmin, request, queryset):
    filename = 'Record.csv'
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)

    writer = csv.writer(response)
    writer.writerow(['created_at', 'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state',
                     'zipcode'])

    for obj in queryset:
        writer.writerow([str(obj.created_at), str(obj.first_name), str(obj.last_name), str(obj.email), str(obj.phone),
                         str(obj.address), str(obj.city),
                         str(obj.state), str(obj.zipcode)])

    return response


admin.site.add_action(export_csv)


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


class RecordAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'zipcode')
    actions = ['export_to_excel']

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv), path('export-csv/', export_csv)]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == 'POST':
            resource = Resource()
            dataset = Dataset()
            new_record = request.FILES['csv_upload']
            imported_data = dataset.load(new_record.read(), format='xlsx')
            for data in imported_data:
                value = Record(
                    data[0],
                    data[1],
                    data[2],
                    data[3],
                    data[4],
                    data[5],
                    data[6],
                    data[7],
                    data[8],
                    data[9],
                )
                value.save()
            url = reverse('admin:index')
            return HttpResponseRedirect(url)

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)

    # def export_csv(self, queryset):
    #     response = HttpResponse(content_type='application/ms-excel')
    #     response['Content-Disposition'] = 'attachment; filename="my_data.xlsx"'
    #     # Create a new Excel workbook and add a worksheet
    #     wb = Workbook()
    #     ws = wb.active
    #     # Add headers to the worksheet
    #     headers = ['created_at', 'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state',
    #                'zipcode']
    #     ws.append(headers)
    #     # Add data to the worksheet
    #     for obj in queryset:
    #         data = [obj.created_at, obj.first_name, obj.last_name, obj.email, obj.phone, obj.address, obj.city,
    #                 obj.state, obj.zipcode]
    #         ws.append(data)
    #     # Save the workbook to the response
    #     wb.save(response)
    #     return response
    #
    # export_csv.short_description = "Export selected records to Excel"


admin.site.register(Record, RecordAdmin)
