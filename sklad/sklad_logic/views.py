from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .models import Products, Categories
from .forms import ProductForm, CategoryForm

class AddProductView(CreateView):
    model = Products
    form_class =  ProductForm
    template_name = "sklad_logic/add_product.html"
    success_url = reverse_lazy("products_list")

class ListProductView(ListView):
    model = Products
    template_name = "sklad_logic/list_product.html"
    context_object_name = "object_list"

class AddCategoryView(CreateView):
    model = Categories
    form_class = CategoryForm
    template_name = "sklad_logic/add_category.html"
    success_url = reverse_lazy("products_list")