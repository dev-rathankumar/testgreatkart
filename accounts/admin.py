from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, UserProfile
from django.utils.html import format_html


# ADMIN PANEL CUSTOMIZATION - ACCOUNTS 

class AccountAdmin(UserAdmin):

    # CUSTOMISE ITEMS TO DISPLAY
    list_display = ('email', 'first_name', 'last_name',  'username', 'date_joined', 'last_login', 'is_active')

    # CUSTOMISE ITEMS TO LINK
    list_display_links = ('email', 'first_name', 'last_name')

    # CUSTOMISE ITEMS TO EDIT
    readonly_fields = ('date_joined', 'last_login')

    # CUSTOMISE ITEMS TO SEARCH
    ordering = ('-date_joined',)
    # CUSTOMISE ITEMS TO FILTER
    filter_horizontal = ()
    # CUSTOMISE ITEMS TO SEARCH
    list_filter = ()

    # CUSTOMISE ITEMS TO ADD TO FORM
    fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="40" style="border-radius: 50%;">'.format(object.profile_picture.url))
    
    thumbnail.short_description = 'Profile Picture'

    list_display = ('thumbnail', 'user', 'city', 'state', 'country')


# CUSTOMISE ADMIN PANEL HEADER
admin.site.site_header = 'SingleVendor Admin'

# REGISTER ACCOUNT MODEL
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)