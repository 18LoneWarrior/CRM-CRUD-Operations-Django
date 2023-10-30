from django.contrib import admin
import csv
from .forms import RecordSearchForm
from .models import Record
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django import forms
from tablib import Dataset


# Register your models here.

# admin.site.register(Record)

def export_csv(modeladmin, request, queryset):
    filename = 'Record.csv'
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)

    writer = csv.writer(response)
    writer.writerow(['id', 'created_at', 'first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state',
                     'zipcode'])

    for obj in queryset:
        writer.writerow(
            [str(obj.id), str(obj.created_at), str(obj.first_name), str(obj.last_name), str(obj.email), str(obj.phone),
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
        new_urls = [path('upload-csv/', self.upload_csv, name='upload_csv'),
                    path('export-csv/', export_csv),
                    path('upload-csv/confirm/', self.confirm_import, name='confirm_import'),
                    path('upload-csv/review/', self.data_preview, name='data_preview'),
                    path('search-view/', self.search_view, name='search-view'),
                    path('search/', self.search, name='search'),
                    path('search-filter/', self.search_filter, name='search-filter'),]
        return new_urls + urls

    def upload_csv(self, request):
        if request.method == 'POST':
            dataset = Dataset()
            new_record = request.FILES['csv_upload']
            imported_data = dataset.load(new_record.read(), format='xlsx')
            # Store the imported data in session for review
            request.session['imported_data'] = list(imported_data)
            return HttpResponseRedirect(reverse('admin:confirm_import'))

        form = CsvImportForm()
        data = {"form": form, "title": "Import CSV Data"}
        return render(request, "admin/app/csv_upload.html", data)

    def confirm_import(self, request):
        if request.method == 'POST':
            selected_records = request.POST.getlist('import_record')
            print("123", selected_records)
            imported_data = request.session.get('imported_data', [])
            print("456", imported_data)
            selected_data = []

            for index in selected_records:
                index = int(index)
                if 0 <= index < len(imported_data):
                    selected_data.append(imported_data[index])
                    print("selected_data========>>>", selected_data)

        imported_data = request.session.get('imported_data', [])
        records = [data for data in imported_data]

        return render(
            request,
            "admin/app/csv_import_confirmation.html",
            {"records": records},
        )

    def data_preview(self, request):
        if request.method == 'POST':
            selected_records = request.POST.getlist('import_record')
            print("+++++++++++++++++++++++", selected_records)
            imported_data = request.session.get('imported_data', [])
            print("__________________________", imported_data)
            selected_data = []
            # for data in imported_data:
            #     if data in selected_records:
            #         selected_data.append(data)

            for index in selected_records:
                index = int(index)
                if 0 <= index < len(imported_data):
                    selected_data.append(imported_data[index])

            if 'confirm' in request.POST:
                for data in selected_data:
                    Record.objects.create(
                        id=data[0],
                        created_at=data[1],
                        first_name=data[2],
                        last_name=data[3],
                        email=data[4],
                        phone=data[5],
                        address=data[6],
                        city=data[7],
                        state=data[8],
                        zipcode=data[9],
                    )
                del request.session['imported_data']
                url = reverse('admin:index')
                return HttpResponseRedirect(url)

        imported_data = request.session.get('imported_data', [])
        records = [data for data in imported_data if data in selected_records]
        return render(request, "admin/app/csv_review.html", {"records": selected_data}, )

    def search(self, request):
        form = RecordSearchForm()
        return render(request, 'admin/app/records.html', {'form': form})

    def search_view(self, request):
        search_text = request.GET.get('search')
        if search_text:
            results = Record.objects.filter(first_name__icontains=search_text)
        else:
            results = []
        context = {"results": results}
        return render(request, 'admin/app/results.html', context)

    def search_filter(self, request):
        if request.method == 'GET':
            form = RecordSearchForm()
            city = request.GET.get('city')
            state = request.GET.get('state')
            if city or state:
                results = Record.objects.filter(city=city) or Record.objects.filter(state=state)
            else:
                results = []
            context = {"results": results}
        return render(request, 'admin/app/results.html', context)


admin.site.register(Record, RecordAdmin)


