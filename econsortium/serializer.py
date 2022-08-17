from rest_framework import serializers 
from .models import consumable_asset 

class consumable_assetserializers(serializers.ModelSerializer): 
    class meta: 
        model=consumable_asset 
        fields='__all__'
