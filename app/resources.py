from import_export import resources
from .models import Record


class Resource(resources.ModelResource):
    class Meta:
        model = Record
