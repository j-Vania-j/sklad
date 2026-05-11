from django.urls import path
from .views import (
    LandingView, DashboardView, AddProductView, ListProductView,
    AddCategoryView, ListCategoriesView,
    ListWarehousesView, AddWarehouseView,
    ListSuppliersView, AddSupplierView,
    StockBalancesView, ProductBatchesView,
    IncomingStockView, OutgoingStockView, StockTransferView,
    TransactionHistoryView, ReportsView,
)


app_name = "sklad_logic"
urlpatterns = [
    path("landing/", LandingView.as_view(), name="landing"),
    path("", DashboardView.as_view(), name="dashboard"),

    # Товары и категории
    path("products/", ListProductView.as_view(), name="products_list"),
    path("products/add/", AddProductView.as_view(), name="products_add"),
    path("products/<int:product_id>/batches/", ProductBatchesView.as_view(), name="product_batches"),
    path("categories/", ListCategoriesView.as_view(), name="categories_list"),
    path("categories/add/", AddCategoryView.as_view(), name="add_category"),

    # Склады
    path("warehouses/", ListWarehousesView.as_view(), name="warehouses_list"),
    path("warehouses/add/", AddWarehouseView.as_view(), name="warehouse_add"),

    # Поставщики
    path("suppliers/", ListSuppliersView.as_view(), name="suppliers_list"),
    path("suppliers/add/", AddSupplierView.as_view(), name="supplier_add"),

    # Остатки
    path("stock/", StockBalancesView.as_view(), name="stock_balances"),

    # Приход/Расход/Перемещение
    path("incoming/", IncomingStockView.as_view(), name="incoming_stock"),
    path("outgoing/", OutgoingStockView.as_view(), name="outgoing_stock"),
    path("transfer/", StockTransferView.as_view(), name="stock_transfer"),

    # История
    path("history/", TransactionHistoryView.as_view(), name="transaction_history"),

    # Отчеты
    path("reports/", ReportsView.as_view(), name="reports"),
]