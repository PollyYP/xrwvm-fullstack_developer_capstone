"""
Admin configurations for the Django app.

This module defines the admin panel behavior for CarModel and CarMake models,
including custom inline configurations and model-specific display settings.
"""

from django.contrib import admin
from .models import CarMake, CarModel


# CarModelInline class
class CarModelInline(admin.TabularInline):
    """
    Inline admin configuration for CarModel.

    Allows CarModel instances to be managed directly within the CarMake admin panel.
    """
    model = CarModel
    extra = 1


# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CarModel model.

    Provides customizations for managing CarModel instances in the admin panel.
    """
    list_display = ('name', 'type', 'year', 'car_make')
    list_filter = ('car_make', 'type', 'year')
    search_fields = ('name', 'car_make__name')


# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CarMake model.

    Allows the management of CarMake instances in the admin panel
    with support for displaying related CarModels inline.
    """
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    inlines = [CarModelInline]


# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
