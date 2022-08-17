import os
from econsortium.models import *
from django.shortcuts import *
from django.http import HttpResponse
import csv
from .forms import *
from .forms import IssueForm, ReceiveForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import *
import pandas as pd

import numpy as np
import io
import urllib, base64
from django.core.files.storage import FileSystemStorage

from .serializer import consumable_assetserializers 
from rest_framework import viewsets  
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


# Create your views here.

def home(request):
    title = 'E-Governance and Prediction of Consortia Resource'
    form = ''
    context = {
	"title": title,
    "test": form,
	}
    return render(request, "home.html",context)

@login_required
#@permission_required('templates/list_items.html')
def list_item(request):

	header = 'List of Items'
	form = assetSearchForm(request.POST or None)
	queryset = consumable_asset.objects.all()
	context = {
		"header": header,
		"queryset": queryset,
		"form": form,
	}

	if request.method == 'POST':
		category = form['category'].value()
		queryset = consumable_asset.objects.filter(item_name__icontains=form['item_name'].value())
		if (category != ''):
			queryset = queryset.filter(category_id=category)

		if form['export_to_CSV'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
			writer = csv.writer(response)
			writer.writerow(['REORDER','QUANTITY','CATEGORY', 'ITEM NAME','LAST UPDATED'])
			instance = queryset
			for stock in instance:
				writer.writerow([stock.reorder_level,stock.quantity,stock.category, stock.item_name,stock.last_updated])
			return response
			
		context = {
		"form": form,
		"header": header,
		"queryset": queryset,
	}
	if request.user.is_superuser:
		return render(request, "list_items.html", context)
	else:
		return render(request, "user_list.html", context)


@login_required
#@permission_required('templates/add_item.html')
def add_items(request):
	if request.user.is_superuser:
		form = assetCreateForm(request.POST or None)
		##check for validation
		if form.is_valid():
			form.save()
			messages.success(request, 'Asset Successfully Added')
			return redirect('/list_item')
		context = {
			"form": form,
			"title": "Add Item",
		}
		return render(request, "add_item.html", context)
	else:
		return render(request, "error.html")



@login_required
#@permission_required('templates/list_item.html')
def update_items(request, pk):
	#queryset = consumable_asset.objects.get(id=pk)
	try:
		queryset = consumable_asset.objects.get(id=pk)
	except consumable_asset.DoesNotExist:
		queryset = None
	form = assetUpdateForm(instance=queryset)
	if request.method == 'POST':
		form = assetUpdateForm(request.POST, instance=queryset)
		if form.is_valid():
			form.save()
			messages.success(request, 'Asset Successfully Updated')
			return redirect('/list_item')
	context = {
		'form':form
	}
	return render(request, 'add_item.html', context)

#@permission_required('templates/delete_items.html')
def delete_items(request, pk):
	queryset = consumable_asset.objects.get(id=pk)
	if request.method == 'POST':
		queryset.delete()
		messages.success(request, 'Asset Successfully Deleted')
		return redirect('/list_item')
	return render(request, 'delete_items.html')

#@permission_required('templates/asset_detail.html')
def asset_detail(request, pk):
	queryset = consumable_asset.objects.get(id=pk)
	context = {
		"title": queryset.item_name,
		"queryset": queryset,
	}
	if request.user.is_superuser:
		return render(request, "asset_detail.html", context)
	else:
		return render(request, "user_asset_detail.html", context)


def issue_items(request, pk):
	queryset = consumable_asset.objects.get(id=pk)
	form = IssueForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity -= instance.issue_quantity
		instance.receive_quantity=0
		instance.receive_by="None"
		instance.taken_quantity=0
		instance.taken_by="None"
		instance.issue_by = str(request.user)
		instance.save()


		issue_history = AssetHistory(
			last_updated = instance.last_updated,
			category_id = instance.category_id,
			item_name = instance.item_name, 
			quantity = instance.quantity, 
			issue_to = instance.issue_to, 
			issue_by = instance.issue_by, 
			receive_quantity= instance.receive_quantity,
			receive_by=instance.receive_by,
			taken_by=instance.taken_by,
			taken_quantity=instance.taken_quantity,
			issue_quantity = instance.issue_quantity, 
		)
		issue_history.save()
		if instance.quantity >= 0:
			messages.success(request, "Issued SUCCESSFULLY. " 
			+ str(instance.quantity) + " " 
			+ str(instance.item_name) + 
			"s now left in Store")
			instance.save()
		else:
			messages.error(request, "Insufficient asset")
		instance.receive_quantity=0
		return redirect('/asset_detail/'+str(instance.id))

			

		# return HttpResponseRedirect(instance.get_absolute_url())

	context = {
		"title": 'Issue ' + str(queryset.item_name),
		"queryset": queryset,
		"form": form,
		"username": 'Issue By: ' + str(request.user),
	}
	return render(request, "add_item.html", context)


def user_issue_items(request, pk):
	queryset = consumable_asset.objects.get(id=pk)
	form = UserIssueForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.quantity -= instance.taken_quantity
		instance.receive_quantity=0
		instance.receive_by="None"
		instance.issue_quantity=0
		instance.issue_to="None"
		instance.save()
		instance.issue_by = str(request.user)


		issue_history = AssetHistory(
			last_updated = instance.last_updated,
			category_id = instance.category_id,
			item_name = instance.item_name, 
			quantity = instance.quantity, 
			issue_to = instance.issue_to,
			receive_quantity= instance.receive_quantity,
			receive_by=instance.receive_by,
			issue_by = instance.issue_by, 
			issue_quantity = instance.issue_quantity,
			taken_by=instance.taken_by,
			taken_quantity=instance.taken_quantity, 
		)
		issue_history.save()

		if instance.quantity >= 0:
			messages.success(request, "Issued SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in Store")
			instance.save()
		else:
			messages.error(request, "Insufficient asset")
			instance.receive_quantity=0

		return redirect('/asset_detail/'+str(instance.id))

			

		# return HttpResponseRedirect(instance.get_absolute_url())

	context = {
		"title": 'Issue ' + str(queryset.item_name),
		"queryset": queryset,
		"form": form,
		"username": 'Issue By: ' + str(request.user),
	}
	return render(request, "add_item.html", context)




def receive_items(request, pk):
	queryset = consumable_asset.objects.get(id=pk)
	form = ReceiveForm(request.POST or None, instance=queryset)
	if form.is_valid():

		instance = form.save(commit=False)
		instance.issue_quantity=0
		instance.taken_by="None"
		instance.taken_quantity=0
		instance.recieve_by="None"
		instance.recieve_quantity=0
		instance.quantity += instance.receive_quantity
		
		if instance.quantity >= 0:
			messages.success(request, "Received SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name)+"s now in Store")
			instance.save()
		else:
			messages.error(request, "Insufficient asset")

		receive_history =  AssetHistory(
			last_updated = instance.last_updated,
			issue_quantity=instance.issue_quantity,
			category_id = instance.category_id,
			item_name = instance.item_name, 
			quantity = instance.quantity, 
			taken_by=instance.taken_quantity,
			taken_quantity = instance.taken_quantity,
			receive_quantity = instance.receive_quantity, 
			receive_by = instance.receive_by
		)
		receive_history.save()
		return redirect('/asset_detail/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())
	context = {
			"title": 'Receive ' + str(queryset.item_name),
			"instance": queryset,
			"form": form,
			"username": 'Receive By: ' + str(request.user),
		}
	return render(request, "add_item.html", context)

def reorder_level(request, pk):
	queryset = consumable_asset.objects.get(id=pk)
	form = ReorderLevelForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Reorder level for " + str(instance.item_name) + " is updated to " + str(instance.reorder_level))

		return redirect("/list_item")
	context = {
			"instance": queryset,
			"form": form,
		}
	return render(request, "add_item.html", context)



def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user, backend='django.contrib.auth.backends.ModelBackend')
			messages.success(request, "Registration successful." )
			return render(request, "home.html")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="register.html", context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user, backend='django.contrib.auth.backends.ModelBackend')
				messages.info(request, f"You are now logged in as {username}.")
				return render(request, "home.html")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return render(request, "home.html")

@login_required
def list_history(request):
	header = 'HISTORY'
	queryset = AssetHistory.objects.all()
	form = AssetHistorySearchForm(request.POST or None)
	context = {
		"form": form,
		"header": header,
		"queryset": queryset,
		
	}
	if request.method == 'POST':
		category = form['category'].value()
		queryset = AssetHistory.objects.filter(
							item_name__icontains=form['item_name'].value()
							)
		if (category != ''):
			queryset = queryset.filter(category_id=category)

		if form['export_to_CSV'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="Asset History.csv"'
			writer = csv.writer(response)
			writer.writerow(
				['CATEGORY', 
				'ITEM NAME',
				'QUANTITY', 
				'ISSUE QUANTITY',
				'ISSUE BY',  
				'RECEIVE QUANTITY', 
				'RECEIVE BY',
				'TAKEN BY',
				'TAKEN QUANITTY'
				'LAST UPDATED'])
			instance = queryset
			for instance in instance:
				writer.writerow(
				[instance.category, 
				instance.item_name, 
				instance.quantity,
				instance.issue_quantity,
				instance.issue_by,  
				instance.receive_quantity, 
				instance.receive_by,
				instance.taken_by,
				instance.taken_quantity,
				instance.last_updated])
			return response

		context = {
		"form": form,
		"header": header,
		"queryset": queryset,
	}

	if request.user.is_superuser:
		return render(request, "list_history.html",context)
	else:
		return render(request, "list_user_history.html",context)

@login_required
def add_category(request):

	form = CategoryCreateForm(request.POST or None)
	if form.is_valid():
		form.save()
		messages.success(request, 'Successfully Created')
		return redirect('/list_item')
	context = {
		"form": form,
		"title": "Add Category",
	}
	if request.user.is_superuser:
		return render(request, "add_item.html", context)
	else:
		return render(request, "error.html")

@login_required
def pie_chart(request):
    labels = []
    data = []

    queryset = consumable_asset.objects.order_by('-quantity')
    for ca in queryset:
        labels.append(ca.item_name)
        data.append(ca.quantity)

    return render(request, 'pie_chart.html', {
        'labels': labels,
        'data': data,
    })

@login_required
def bar_chart(request):
    labels= []
    ts = []
    data = []

    queryset = consumable_asset.objects.order_by('-quantity')
    for ca in queryset:
        labels.append(ca.item_name)
        data.append(ca.quantity)
        ts.append(ca.last_updated)

    return render(request, 'bar_chart.html', {
        'labels': labels,
        'data': data,
		'ts' : ts,
    })

@login_required
def radar_chart(request):
    labels = []
    data = []

    queryset = consumable_asset.objects.order_by('-quantity')
	
    for ca in queryset:
        labels.append(ca.item_name)
        data.append(ca.quantity)

    return render(request, 'radar_chart.html', {
        'labels': labels,
        'data': data,
    })

@login_required
def polar_chart(request):
    labels = []
    data = []

    queryset = consumable_asset.objects.order_by('-quantity')
    for ca in queryset:
        labels.append(ca.item_name)
        data.append(ca.quantity)

    return render(request, 'polar_area.html', {
        'labels': labels,
        'data': data,
    })

@login_required
def line_chart(request):
    labels = []
    ts = []
    data = []

    queryset = consumable_asset.objects.order_by('-quantity')
    for ca in queryset:
        labels.append(ca.item_name)
        data.append(ca.quantity)
        ts.append(ca.last_updated)

        #print(ts)

    return render(request, 'line_chart.html', {
        'labels': labels,
        'data': data,
		'ts' : ts,
    })

class CustomerView(viewsets.ModelViewSet): 
    queryset = consumable_asset.objects.all() 
    serializer_class = consumable_assetserializers

def upload_csv(request):
    
	if request.method == 'POST': 
		form = DocumentForm(request.POST, request.FILES) 
		if form.is_valid():
			myfile = request.FILES['myfile']
			fs = FileSystemStorage()
			filename = fs.save(myfile.name, myfile)
			uploaded_file_url = fs.url(filename)
			#uploaded_file_url = 'https://raw.githubusercontent.com/Nithesh1501/Econsortium/master/List of stock.csv'
			#uploaded_file_url = fs.url(filename)
			uploaded_file_url = 'https://raw.githubusercontent.com/Nithesh1501/Econsortium/master/List of stock.csv'
			messages.success(request, 'Successfully Uploaded, Now click the below button to predict the data')
			return render(request, 'upload_csv.html', {
				'uploaded_file_url': uploaded_file_url
			})
    
	else: 
		form = DocumentForm()
    
	return render(request, 'upload_csv.html', {
        'form': form
    })


def sigmoid(x, Beta_1, Beta_2):
	y = 1 / (1 + np.exp(-Beta_1*(x-Beta_2)))
	return y


import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

def linear(request):
	dataset = pd.read_csv('List of stock.csv',usecols=[0,1], header=0)
	dataset.head()
	
	# data preprocessing
	x_data = dataset.iloc[:, :-1].values.flatten()  #independent variable array
	y_data = dataset.iloc[:,1].values.flatten()  #dependent variable vector
		
	beta_1 = 100.0
	beta_2 = 12200.0

	#logistic function
	Y_pred = sigmoid(x_data, beta_1 , beta_2)
	#plot initial prediction against datapoints
	plt.plot(x_data, Y_pred*15000000000000)
	plt.plot(x_data, y_data)

	xdata =x_data/max(x_data)
	ydata =y_data/max(y_data)
	
	from scipy.optimize import curve_fit
	popt, pcov = curve_fit(sigmoid, xdata, ydata)
	print("optimised parameter",popt)
	# Now we plot resulting regression model.
	x = np.linspace(1, 22, 100)
	x = x/max(x)
	plt.figure(figsize=(8,5))
	y = sigmoid(x, *popt)
	plt.plot(xdata, ydata, 'rd', label='data')
	plt.plot(x,y, linewidth=5.0, label='fit')
	plt.legend(loc='best')
	plt.title('Quantity vs Reorder')
	plt.ylabel('Reorder')
	plt.xlabel('Quantity')
	buf0 = io.BytesIO()
	plt.savefig(buf0, format='png')

	plt.tight_layout()
	buf0.seek(0)
	string0 = base64.b64encode(buf0.read())
	uri0= 'data:image/png;base64,' + urllib.parse.quote(string0)
	
	image_base64_0 = base64.b64encode(buf0.getvalue()).decode('utf-8').replace('\n', '')
	buf0.close()
	
	if os.path.exists("List of stock.csv"):
		os.remove("List of stock.csv")

	slope_intercept = np.polyfit(x_data,y_data,1)
	print(slope_intercept)
	# split data into train/test
	# msk = np.random.rand(len(dataset)) < 0.8
	# train_x = xdata[msk]
	# test_x = xdata[~msk]
	# train_y = ydata[msk]
	# test_y = ydata[~msk]
	# # build the model using train set
	# popt, pcov = curve_fit(sigmoid, train_x, train_y)
	# # predicting using test set
	# y_hat = sigmoid(test_x, *popt)
	# # evaluation
	# print("Mean absolute error: %.2f" % np.mean(np.absolute(y_hat - test_y)))
	# print("Residual sum of squares (MSE): %.2f" % np.mean((y_hat - test_y) ** 2))
	# from sklearn.metrics import r2_score
	# print("R2-score: %.2f" % r2_score(y_hat , test_y))
	return render(request,'linear.html',{'data_0':uri0,'image_base64_0':image_base64_0})
	
