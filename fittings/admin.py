from django.contrib import admin
from django.db.models import Count

from .forms import CategoryForm
from .models import Fitting, Category

# Register your models here.
admin.site.register(Fitting)


class CategoryAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ('name', 'color', 'restricted', )
    list_filter = ('groups',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # TODO: Figure out how to get an accurate Fitting count to include doctrine fits.

        qs = qs.annotate(
            fittings_count=Count('fittings'),
            doctrine_count=Count('doctrines'),
            groups_count=Count('groups'),
        )

        return qs

    search_fields = ('name', 'color')

    def restricted(self, obj):
        return obj.groups.exists()

    restricted.boolean = True



    form = CategoryForm
    filter_horizontal = ('fittings', 'doctrines', 'groups')


admin.site.register(Category, CategoryAdmin)
