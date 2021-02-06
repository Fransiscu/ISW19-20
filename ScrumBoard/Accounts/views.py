from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.
from .forms import CreateUserForm


def registerPage(request):
    form = CreateUserForm

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'L\'account di ' + user + ' è stato creato con successo!')
            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # se già loggato si va alla dashboard direttamente

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, 'Username o password errati')

    context = {}
    return render(request, 'login.html', context)


def logoutUser(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


def home(request):
    return render(request, 'login.html')
