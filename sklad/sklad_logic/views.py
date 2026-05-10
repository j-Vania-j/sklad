from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, FormView
from django.db import connection, transaction
from .models import Products, Categories, Warehouses, Suppliers, Batches, Transactions
from .forms import ProductForm, CategoryForm, WarehouseForm, SupplierForm


class DashboardView(TemplateView):
    template_name = "sklad_logic/dashboard.html"


class AddProductView(CreateView):
    model = Products
    form_class = ProductForm
    template_name = "sklad_logic/add_product.html"
    success_url = reverse_lazy("sklad_logic:products_list")


class ListProductView(ListView):
    model = Products
    template_name = "sklad_logic/list_product.html"
    context_object_name = "products"
    paginate_by = 50

    def get_queryset(self):
        qs = Products.objects.select_related("category").all()
        cat = self.request.GET.get("category")
        search = self.request.GET.get("search")
        if cat:
            with connection.cursor() as cursor:
                cursor.execute("""
                    WITH RECURSIVE subcats AS (
                        SELECT id FROM sklad_logic_categories WHERE id = %s
                        UNION ALL
                        SELECT c.id FROM sklad_logic_categories c
                        JOIN subcats s ON c.parent_id = s.id
                    )
                    SELECT id FROM subcats
                """, [cat])
                cat_ids = [row[0] for row in cursor.fetchall()]
            qs = qs.filter(category_id__in=cat_ids)
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE cat_tree AS (
                    SELECT id, name, parent_id, 0 AS level, CAST(id AS TEXT) AS path
                    FROM sklad_logic_categories WHERE parent_id IS NULL
                    UNION ALL
                    SELECT c.id, c.name, c.parent_id, ct.level + 1,
                           ct.path || '->' || c.id
                    FROM sklad_logic_categories c
                    JOIN cat_tree ct ON c.parent_id = ct.id
                )
                SELECT id, name, level FROM cat_tree ORDER BY path
            """)
            rows = cursor.fetchall()
        ctx["categories_tree"] = [{"id": r[0], "name": "— " * r[2] + r[1]} for r in rows]
        ctx["selected_category"] = self.request.GET.get("category", "")
        ctx["search_query"] = self.request.GET.get("search", "")
        return ctx


class AddCategoryView(CreateView):
    model = Categories
    form_class = CategoryForm
    template_name = "sklad_logic/add_category.html"
    success_url = reverse_lazy("sklad_logic:products_list")


class ListCategoriesView(ListView):
    model = Categories
    template_name = "sklad_logic/list_category.html"
    context_object_name = "categories"

    def get_queryset(self):
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE cat_tree AS (
                    SELECT id, name, parent_id, 0 AS level, CAST(id AS TEXT) AS path
                    FROM sklad_logic_categories WHERE parent_id IS NULL
                    UNION ALL
                    SELECT c.id, c.name, c.parent_id, ct.level + 1,
                           ct.path || '->' || c.id
                    FROM sklad_logic_categories c
                    JOIN cat_tree ct ON c.parent_id = ct.id
                )
                SELECT id, name, level, parent_id FROM cat_tree ORDER BY path
            """)
            return [{"id": r[0], "name": r[1], "level": r[2], "parent_id": r[3]}
                    for r in cursor.fetchall()]


# --- Склады ---

class ListWarehousesView(TemplateView):
    template_name = "sklad_logic/list_warehouse.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT w.id, w.name, w.address, w.capacity,
                       COALESCE(SUM(b.quantity), 0) AS total_occupied
                FROM sklad_logic_warehouses w
                LEFT JOIN sklad_logic_batches b ON b.warehouse_id = w.id
                GROUP BY w.id, w.name, w.address, w.capacity
                ORDER BY w.name
            """)
            ctx["warehouses"] = [
                {"id": r[0], "name": r[1], "address": r[2], "capacity": r[3], "occupied": r[4]}
                for r in cursor.fetchall()
            ]
        return ctx


class AddWarehouseView(CreateView):
    model = Warehouses
    form_class = WarehouseForm
    template_name = "sklad_logic/add_warehouse.html"
    success_url = reverse_lazy("sklad_logic:warehouses_list")


# --- Поставщики ---

class ListSuppliersView(ListView):
    model = Suppliers
    template_name = "sklad_logic/list_supplier.html"
    context_object_name = "suppliers"


class AddSupplierView(CreateView):
    model = Suppliers
    form_class = SupplierForm
    template_name = "sklad_logic/add_supplier.html"
    success_url = reverse_lazy("sklad_logic:suppliers_list")


# --- Остатки по складам ---

class StockBalancesView(TemplateView):
    template_name = "sklad_logic/stock_balances.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        warehouse_id = self.request.GET.get("warehouse")
        with connection.cursor() as cursor:
            if warehouse_id:
                cursor.execute("""
                    SELECT p.id, p.name, p.sku, w.name, COALESCE(SUM(b.quantity), 0)
                    FROM sklad_logic_products p
                    JOIN sklad_logic_batches b ON b.product_id = p.id
                    JOIN sklad_logic_warehouses w ON b.warehouse_id = w.id
                    WHERE w.id = %s
                    GROUP BY p.id, p.name, p.sku, w.name
                    HAVING SUM(b.quantity) > 0
                    ORDER BY p.name
                """, [warehouse_id])
            else:
                cursor.execute("""
                    SELECT p.id, p.name, p.sku, w.name, COALESCE(SUM(b.quantity), 0)
                    FROM sklad_logic_products p
                    JOIN sklad_logic_batches b ON b.product_id = p.id
                    JOIN sklad_logic_warehouses w ON b.warehouse_id = w.id
                    GROUP BY p.id, p.name, p.sku, w.name
                    HAVING SUM(b.quantity) > 0
                    ORDER BY p.name, w.name
                """)
            ctx["stocks"] = [
                {"product_id": r[0], "product": r[1], "sku": r[2], "warehouse": r[3], "quantity": r[4]}
                for r in cursor.fetchall()
            ]
            cursor.execute("SELECT id, name FROM sklad_logic_warehouses ORDER BY name")
            ctx["warehouses"] = [{"id": r[0], "name": r[1]} for r in cursor.fetchall()]
        ctx["selected_warehouse"] = warehouse_id or ""
        return ctx


# --- Партии товара ---

class ProductBatchesView(TemplateView):
    template_name = "sklad_logic/product_batches.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product_id = kwargs.get("product_id")
        product = get_object_or_404(Products, id=product_id)
        ctx["product"] = product
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.id, w.name, COALESCE(s.name, '—'), b.quantity,
                       b.purchase_price, b.expire_date, b.created_at
                FROM sklad_logic_batches b
                JOIN sklad_logic_warehouses w ON b.warehouse_id = w.id
                LEFT JOIN sklad_logic_suppliers s ON b.supplier_id = s.id
                WHERE b.product_id = %s AND b.quantity > 0
                ORDER BY b.expire_date ASC
            """, [product_id])
            ctx["batches"] = [
                {"id": r[0], "warehouse": r[1], "supplier": r[2], "quantity": r[3],
                 "price": r[4], "expire": r[5], "created": r[6]}
                for r in cursor.fetchall()
            ]
        return ctx


# --- Приход товара ---

class IncomingStockView(FormView):
    template_name = "sklad_logic/incoming_stock.html"
    success_url = reverse_lazy("sklad_logic:stock_balances")

    def get_form(self):
        from django import forms as f

        class IncomingForm(f.Form):
            product = f.ModelChoiceField(
                queryset=Products.objects.all(),
                label="Товар",
                widget=f.Select(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'})
            )
            warehouse = f.ModelChoiceField(
                queryset=Warehouses.objects.all(),
                label="Склад",
                widget=f.Select(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'})
            )
            supplier = f.ModelChoiceField(
                queryset=Suppliers.objects.all(),
                label="Поставщик",
                required=False,
                widget=f.Select(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'})
            )
            quantity = f.IntegerField(
                label="Количество",
                min_value=1,
                widget=f.NumberInput(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors', 'placeholder': '100'})
            )
            purchase_price = f.FloatField(
                label="Закупочная цена",
                min_value=0,
                widget=f.NumberInput(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors', 'placeholder': '10.50'})
            )
            expire_date = f.DateField(
                label="Срок годности",
                widget=f.DateInput(attrs={'type': 'date', 'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'})
            )

        return IncomingForm(self.request.POST or None)

    def form_valid(self, form):
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sklad_logic_batches
                        (product_id, warehouse_id, supplier_id, quantity, purchase_price, expire_date, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, [
                    form.cleaned_data["product"].id,
                    form.cleaned_data["warehouse"].id,
                    form.cleaned_data["supplier"].id if form.cleaned_data["supplier"] else None,
                    form.cleaned_data["quantity"],
                    form.cleaned_data["purchase_price"],
                    form.cleaned_data["expire_date"],
                ])
                cursor.execute("SELECT currval(pg_get_serial_sequence('sklad_logic_batches', 'id'))")
                batch_id = cursor.fetchone()[0]
                cursor.execute("""
                    INSERT INTO sklad_logic_transactions
                        (batch_id, type, quantity, timestamp, user_id, comment)
                    VALUES (%s, 'IN', %s, NOW(), NULL, 'Приходная накладная')
                """, [batch_id, form.cleaned_data["quantity"]])
        return super().form_valid(form)


# --- Расход товара (FEFO) ---

class OutgoingStockView(FormView):
    template_name = "sklad_logic/outgoing_stock.html"
    success_url = reverse_lazy("sklad_logic:stock_balances")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.id, p.name, w.id, w.name, SUM(b.quantity)
                FROM sklad_logic_batches b
                JOIN sklad_logic_products p ON b.product_id = p.id
                JOIN sklad_logic_warehouses w ON b.warehouse_id = w.id
                WHERE b.quantity > 0
                GROUP BY p.id, p.name, w.id, w.name
                ORDER BY p.name, w.name
            """)
            ctx["available_stock"] = [
                {"product_id": r[0], "product": r[1], "warehouse_id": r[2], "warehouse": r[3], "qty": r[4]}
                for r in cursor.fetchall()
            ]

            cursor.execute("""
                SELECT p.name, w.name, b.id, b.quantity, b.expire_date, b.purchase_price
                FROM sklad_logic_batches b
                JOIN sklad_logic_products p ON b.product_id = p.id
                JOIN sklad_logic_warehouses w ON b.warehouse_id = w.id
                WHERE b.quantity > 0
                ORDER BY p.name, w.name, b.expire_date ASC
            """)
            ctx["batches_detail"] = [
                {"product": r[0], "warehouse": r[1], "id": r[2], "qty": r[3], "expire": r[4], "price": r[5]}
                for r in cursor.fetchall()
            ]
        return ctx

    def get_form(self):
        from django import forms as f

        class OutgoingForm(f.Form):
            product = f.ModelChoiceField(
                queryset=Products.objects.all(),
                label="Товар",
                widget=f.Select(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'})
            )
            warehouse = f.ModelChoiceField(
                queryset=Warehouses.objects.all(),
                label="Со склада",
                widget=f.Select(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'})
            )
            quantity = f.IntegerField(
                label="Количество",
                min_value=1,
                widget=f.NumberInput(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors', 'placeholder': '50'})
            )

        return OutgoingForm(self.request.POST or None)

    def form_valid(self, form):
        product = form.cleaned_data["product"]
        warehouse = form.cleaned_data["warehouse"]
        needed = form.cleaned_data["quantity"]

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, quantity, purchase_price
                    FROM sklad_logic_batches
                    WHERE product_id = %s AND warehouse_id = %s AND quantity > 0
                    ORDER BY expire_date ASC, created_at ASC
                    FOR UPDATE
                """, [product.id, warehouse.id])
                batches = cursor.fetchall()

                total = sum(b[1] for b in batches)
                if total < needed:
                    form.add_error("quantity", f"Недостаточно товара на складе. Доступно: {total}")
                    return self.form_invalid(form)

                remaining = needed
                for batch_id, qty, price in batches:
                    if remaining <= 0:
                        break
                    take = min(qty, remaining)
                    cursor.execute("UPDATE sklad_logic_batches SET quantity = quantity - %s WHERE id = %s", [take, batch_id])
                    cursor.execute("""
                        INSERT INTO sklad_logic_transactions (batch_id, type, quantity, timestamp, user_id, comment)
                        VALUES (%s, 'OUT', %s, NOW(), NULL, 'Расходная накладная')
                    """, [batch_id, take])
                    remaining -= take

        return super().form_valid(form)


# --- Перемещение между складами ---

class StockTransferView(FormView):
    template_name = "sklad_logic/stock_transfer.html"
    success_url = reverse_lazy("sklad_logic:stock_balances")

    def get_form(self):
        from django import forms as f

        class TransferForm(f.Form):
            product = f.ModelChoiceField(
                queryset=Products.objects.all(),
                label="Товар",
                widget=f.Select(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'})
            )
            from_warehouse = f.ModelChoiceField(
                queryset=Warehouses.objects.all(),
                label="Со склада",
                widget=f.Select(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'})
            )
            to_warehouse = f.ModelChoiceField(
                queryset=Warehouses.objects.all(),
                label="На склад",
                widget=f.Select(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'})
            )
            quantity = f.IntegerField(
                label="Количество",
                min_value=1,
                widget=f.NumberInput(attrs={'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors', 'placeholder': '50'})
            )

        return TransferForm(self.request.POST or None)

    def form_valid(self, form):
        product = form.cleaned_data["product"]
        from_wh = form.cleaned_data["from_warehouse"]
        to_wh = form.cleaned_data["to_warehouse"]
        needed = form.cleaned_data["quantity"]

        if from_wh == to_wh:
            form.add_error("to_warehouse", "Склады должны различаться")
            return self.form_invalid(form)

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, quantity, purchase_price
                    FROM sklad_logic_batches
                    WHERE product_id = %s AND warehouse_id = %s AND quantity > 0
                    ORDER BY expire_date ASC, created_at ASC
                    FOR UPDATE
                """, [product.id, from_wh.id])
                batches = cursor.fetchall()

                total = sum(b[1] for b in batches)
                if total < needed:
                    form.add_error("quantity", f"Недостаточно товара на складе-отправителе. Доступно: {total}")
                    return self.form_invalid(form)

                remaining = needed
                for batch_id, qty, price in batches:
                    if remaining <= 0:
                        break
                    take = min(qty, remaining)

                    cursor.execute("UPDATE sklad_logic_batches SET quantity = quantity - %s WHERE id = %s", [take, batch_id])

                    cursor.execute("""
                        INSERT INTO sklad_logic_batches
                            (product_id, warehouse_id, supplier_id, quantity, purchase_price, expire_date, created_at)
                        VALUES (%s, %s, NULL, %s, %s, NOW(), NOW())
                    """, [product.id, to_wh.id, take, price])
                    cursor.execute("SELECT currval(pg_get_serial_sequence('sklad_logic_batches', 'id'))")
                    new_batch_id = cursor.fetchone()[0]

                    cursor.execute("""
                        INSERT INTO sklad_logic_transactions (batch_id, type, quantity, timestamp, user_id, comment)
                        VALUES (%s, 'OUT', %s, NOW(), NULL, 'Перемещение между складами')
                    """, [batch_id, take])
                    cursor.execute("""
                        INSERT INTO sklad_logic_transactions (batch_id, type, quantity, timestamp, user_id, comment)
                        VALUES (%s, 'IN', %s, NOW(), NULL, 'Перемещение между складами')
                    """, [new_batch_id, take])

                    remaining -= take

        return super().form_valid(form)


# --- История движений ---

class TransactionHistoryView(TemplateView):
    template_name = "sklad_logic/transaction_history.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT t.id, t.type, t.quantity, t.timestamp, COALESCE(t.comment, ''),
                       p.name, p.sku, w.name
                FROM sklad_logic_transactions t
                JOIN sklad_logic_batches b ON t.batch_id = b.id
                JOIN sklad_logic_products p ON b.product_id = p.id
                JOIN sklad_logic_warehouses w ON b.warehouse_id = w.id
                ORDER BY t.timestamp DESC
                LIMIT 200
            """)
            ctx["transactions"] = [
                {"id": r[0], "type": r[1], "quantity": r[2], "timestamp": r[3],
                 "comment": r[4], "product": r[5], "sku": r[6], "warehouse": r[7]}
                for r in cursor.fetchall()
            ]
        return ctx


# --- Отчеты ---

class ReportsView(TemplateView):
    template_name = "sklad_logic/reports.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM sklad_logic_products")
            ctx["total_products"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM sklad_logic_batches WHERE expire_date < CURRENT_DATE AND quantity > 0")
            ctx["expired_batches"] = cursor.fetchone()[0]

            cursor.execute("""
                SELECT p.name, SUM(b.quantity)
                FROM sklad_logic_products p
                JOIN sklad_logic_batches b ON b.product_id = p.id
                GROUP BY p.name
                HAVING SUM(b.quantity) < 10
                ORDER BY SUM(b.quantity)
                LIMIT 10
            """)
            ctx["critical_stock"] = [{"name": r[0], "qty": r[1]} for r in cursor.fetchall()]

            cursor.execute("""
                SELECT p.name, COUNT(t.id) as moves,
                       ROW_NUMBER() OVER (ORDER BY COUNT(t.id) DESC) as rank
                FROM sklad_logic_products p
                JOIN sklad_logic_batches b ON b.product_id = p.id
                JOIN sklad_logic_transactions t ON t.batch_id = b.id
                GROUP BY p.name
                ORDER BY moves DESC
                LIMIT 10
            """)
            ctx["top_moving"] = [{"name": r[0], "moves": r[1], "rank": r[2]} for r in cursor.fetchall()]

            cursor.execute("""
                SELECT p.name, w.name, b.purchase_price, b.created_at, b.expire_date
                FROM sklad_logic_batches b
                JOIN sklad_logic_products p ON b.product_id = p.id
                JOIN sklad_logic_warehouses w ON b.warehouse_id = w.id
                WHERE b.expire_date < CURRENT_DATE + INTERVAL '30 days' AND b.quantity > 0
                ORDER BY b.expire_date
            """)
            ctx["expiring_soon"] = [
                {"product": r[0], "warehouse": r[1], "price": r[2], "created": r[3], "expires": r[4]}
                for r in cursor.fetchall()
            ]
        return ctx