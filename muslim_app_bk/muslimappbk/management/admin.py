from django.contrib import admin
from .models import AppCategory, Tag, MobileApp
# from ordered_model.admin import OrderedModelAdmin
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

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass

