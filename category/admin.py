from django.contrib import admin
from .models import Category

# ADMIN PANEL CUSTOMIZATION

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

admin.site.site_header = 'SingleVendor Admin'
admin.site.register(Category, CategoryAdmin)
