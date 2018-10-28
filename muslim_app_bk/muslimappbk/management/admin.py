from django.contrib import admin
from .models import AppCategory, MobileApp, Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin

# Register your models here.

class MobileAppInline(OrderedTabularInline):
    model = MobileApp
    fields = ('name', 'order', 'move_up_down_links')
    readonly_fields = ('name', 'order', 'move_up_down_links')
    extra = 1
    ordering = ('order',)
    
@admin.register(AppCategory)
class AppCategoryAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ('name',)
    inlines = (MobileAppInline,)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'
    
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

