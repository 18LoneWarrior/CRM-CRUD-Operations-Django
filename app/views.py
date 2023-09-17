from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm
from .models import Record
from .resources import Resource
from tablib import Dataset
from django.http import HttpResponse
import pandas as pd


def home(request):
    records = Record.objects.all()
    # Check the permissions for login
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Authenticate the user credentials
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('home')
        else:
            messages.success(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')
    else:
        return render(request, 'home.html', {'records': records})


# Logging out the user
def logout_user(request):
    logout(request)
    messages.success(request, "Logout successfully!")
    return redirect('home')


def register_user(request):
    # Authenticate and save the user in the database
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Authenticate and login
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})

    return render(request, 'register.html', {'form': form})


def customer_record(request, pk):
    if request.user.is_authenticated:
        customer_record = Record.objects.get(id=pk)
        return render(request, 'record.html', {'customer_record': customer_record})
    else:
        messages.success(request, "Login to view the page")
        return redirect('home')


def delete_record(request, pk):
    if request.user.is_authenticated:
        delete_data = Record.objects.get(id=pk)
        delete_data.delete()
        messages.success(request, "Data deleted successfully")
        return redirect('home')
    else:
        messages.error(request, "Login First!")
        return redirect('home')


def add_record(request):
    form = AddRecordForm(request.POST or None)
    if request.user.is_authenticated:
        if request.method == 'POST':
            if form.is_valid():
                record = form.save()
                messages.success(request, "Data Added to DataBase!")
                return redirect('home')
        return render(request, 'add_record.html', {'form': form})
    else:
        messages.error(request, "Login First!")
        return redirect('home')


def update_record(request, pk):
    if request.user.is_authenticated:
        current_record = Record.objects.get(id=pk)
        form = AddRecordForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.error(request, "Data has been Updated!")
            return redirect('home')
        return render(request, 'update_record.html', {'form': form})
    else:
        messages.error(request, "Login First")
        return redirect('home')


def import_record(request):
    records = Record.objects.all()
    if request.method == 'POST':
        resource = Resource()
        dataset = Dataset()
        new_record = request.FILES['import_record']
        imported_data = dataset.load(new_record.read(), format='xlsx')
        for data in imported_data:
            value = Record(
                data[0],
                data[1],
                data[2],
                data[3],
                data[4],
                data[5],
                data[6],
                data[7],
                data[8],
                data[9],
            )
            value.save()

    # messages.success(request, "Dataset imported successfully")
    return render(request, 'import_record.html', {'records': records})


# def confirm_data(request):
#     if request.method == "POST":
#         data = request.POST.getlist("selected_data")
#         for item_id in data:
#             # Find the item by ID and save it to the database
#             item = next(item for item in request.session["excel_data"] if str(item["id"]) == item_id)
#             Record.objects.create(**item)
#         del request.session["excel_data"]  # Remove the data from the session
#         return redirect("admin:excel_import")
#     else:
#         data = request.session.get("excel_data", [])
#         return render(request, "admin/app/confirm.html", {"data": data})
