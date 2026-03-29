from django.urls import path, include
from .views import AddProductView, ListProductView, AddCategoryView


name = "sklad_logic"
urlpatterns = [
    path("products/add/", AddProductView.as_view(), name='products_add'),
    path("products/list/", ListProductView.as_view(), name='products_list' ),
    path("category/add/", AddCategoryView.as_view(), name="add_category" ),
]