from django.contrib import admin

# Register your models here.

from .models import *

from .forms import *

class assetCreateAdmin(admin.ModelAdmin):
   list_display = ['category', 'item_name', 'quantity']
   form = assetCreateForm
   list_filter = ['category']
   search_fields = ['category', 'item_name']

admin.site.register(consumable_asset,assetCreateAdmin)
admin.site.register(Category)