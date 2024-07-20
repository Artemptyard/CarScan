"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from carscan import views

urlpatterns = [
                  path("admin/", admin.site.urls),
                  re_path(r"$", views.main_page),
                  re_path(r"^api/cars/$", views.cars_list),
                  re_path(r"^api/cars/(\d+)$", views.cars_detail),
                  re_path(r"^api/parse/$", views.parse),
                  re_path(r"^api/parse/result/$", views.get_result),
                  # re_path(r"^api/user/(\d+)$", views.students_detail),
                  # re_path(r"^api/users/(\d+)$", views.students_detail),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
