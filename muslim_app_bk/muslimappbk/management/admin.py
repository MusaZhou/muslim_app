from django.contrib import admin
from .models import AppCategory
from .models import Tag

# Register your models here.

@admin.register(AppCategory)
class AppCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
