from django import forms
from django.http import *

from .models import *
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user


class assetCreateForm(forms.ModelForm):
	class Meta:
		model = consumable_asset
		fields = ['category', 'item_name', 'quantity']
	
	def clean_category(self):
		category = self.cleaned_data.get('category')
		if not category:
			raise forms.ValidationError('This field is required')
		
		return category
	
	def clean_quantity(self):
		quantity = self.cleaned_data.get('quantity')
		if quantity<0:
			raise forms.ValidationError('Quanity cannot be negative')
		
		return quantity
    
	def clean_item_name(self):
		item_name = self.cleaned_data.get('item_name')
		if not item_name:
			raise forms.ValidationError('This field is required')
		
		for instance in consumable_asset.objects.all():
			if instance.item_name == item_name:
				raise forms.ValidationError(str(item_name) + ' is already created')
		return item_name

class assetSearchForm(forms.ModelForm):
   export_to_CSV = forms.BooleanField(required=False)
   class Meta:
     model = consumable_asset
     fields = ['category', 'item_name']

class assetUpdateForm(forms.ModelForm):
	class Meta:
		model = consumable_asset
		fields = ['category', 'item_name', 'quantity']

class IssueForm(forms.ModelForm):
	class Meta:
		model = consumable_asset
		fields = ['issue_quantity', 'issue_to']

class UserIssueForm(forms.ModelForm):
	class Meta:
		model = consumable_asset
		fields = ['taken_quantity', 'taken_by']

class ReceiveForm(forms.ModelForm):
	class Meta:
		model = consumable_asset
		fields = ['receive_quantity', 'receive_by']

class ReorderLevelForm(forms.ModelForm):
	class Meta:
		model = consumable_asset
		fields = ['reorder_level']




class AssetHistorySearchForm(forms.ModelForm):
	export_to_CSV = forms.BooleanField(required=False)

	class Meta:
		model = AssetHistory
		fields = ['category', 'item_name']

class AssetHistorySearchForm(forms.ModelForm):
	export_to_CSV = forms.BooleanField(required=False)
	class Meta:
		model = AssetHistory
		fields = ['category', 'item_name']

class CategoryCreateForm(forms.ModelForm):
	class Meta:
		model = Category
		fields = ['name']

class DocumentForm(forms.ModelForm):
    class Meta:
        model = consumable_asset
        fields = ['reorder_level', 'quantity',]