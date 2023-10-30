import django_filters
from .models import *


class SearchFilter(django_filters.FilterSet):
    class Meta:
        model = Record
        fields = '__all__'
        exclude = ['zipcode',
                   'created_at', 'last_name',
                   'email','phone', 'address']
