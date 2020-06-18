"""SISOP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
# from django.contrib import admin
from django.conf.urls import url, include
from django.shortcuts import redirect, reverse

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^sisop$', lambda request: redirect(reverse('auth_sisop:login'), permanent=True)),
    url(r'^general/', include('general.urls')),
    url(r'^espectro/', include('espectro.urls')),
    url(r'^auth/', include('auth_sisop.urls')),
    url(r'^admin/', include('administracion.urls')),
    url(r'^parte_diario/', include('parte_diario.urls'))
]
