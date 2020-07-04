"""ScrumBoard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from ScrumBoard import views
from django.http import HttpResponse

def home(request):
    return HttpResponse('Home page')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hello/', views.hello),
    path(r'dashboard/', views.dashboard),
    path(r'board/<board_id>/', views.showboard, name='show-board'),
    path(r'board/<board_id>/aggiungi_card/<column_id>', views.aggiungi_card, name='add-card'),

    path('', include('Accounts.urls'))

]
