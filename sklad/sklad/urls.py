"""
URL configuration for sklad project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("allauth.urls")),
    path('warehouse/', include("sklad_logic.urls")),
    path("", TemplateView.as_view(template_name="landing.html"), name="landing"),
]
