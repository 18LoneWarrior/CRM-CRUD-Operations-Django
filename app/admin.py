from django.contrib import admin
import csv
from .forms import RecordSearchForm, PersonSearchForm
from .models import Record, Person, City, Country, State
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django import forms
from tablib import Dataset
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string


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
                    path('search-filter/', self.search_filter, name='search-filter'), ]
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


# CUSTOM FILTER SECTION FOR "CITY" AND "STATE" IN PERSON MODEL
class CityFilter(admin.SimpleListFilter):
    title = _('City')
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = City.objects.values_list('id', 'name')
        return cities

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__id=self.value())
        return queryset


class CountryFilter(admin.SimpleListFilter):
    title = _('Country')
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        states = Country.objects.values_list('id', 'name')
        return states

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(state__id=self.value())
        return queryset


# URLS AND VIEWS FOR THE PERSON MODEL WITH CUSTOM SEARCH AND FILTER OPTIONS
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'country', 'state')
    list_filter = (CityFilter, CountryFilter)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('city_choices/', self.city_choices, name='city_choices'), ]
        return my_urls + urls

    def city_choices(self, request):
        state_id = request.GET.get('state', None)
        state = get_object_or_404(State, id=state_id) if state_id else None
        # Get the city choices based on the selected state from the Person model
        persons_in_state = Person.objects.filter(state=state)
        cities = City.objects.filter(person__in=persons_in_state).distinct()
        # Render the HTML for the updated city choices
        html = render_to_string('admin/app/index.html', {'cities': cities})
        return HttpResponse(html)

    def get_changelist_form(self, request, **kwargs):
        form = PersonSearchForm(request.GET)
        return form

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['search_form'] = self.get_changelist_form(request)
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Record, RecordAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(City)
admin.site.register(State)
admin.site.register(Country)
