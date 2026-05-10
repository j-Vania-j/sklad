from django import forms
from django.db import connection
from .models import Products, Categories, Warehouses, Suppliers


class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': 'Например: Coca-Cola 0.5л'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': 'Артикул'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': 'шт, кг, л'
            }),
        }
        labels = {
            'name': 'Наименование товара',
            'sku': 'Артикул (SKU)',
            'category': 'Категория',
            'unit': 'Единица измерения',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].widget = forms.Select(attrs={
            'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'
        })
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE cat_tree AS (
                    SELECT id, name, parent_id, 0 AS level, CAST(id AS TEXT) AS path
                    FROM sklad_logic_categories WHERE parent_id IS NULL
                    UNION ALL
                    SELECT c.id, c.name, c.parent_id, ct.level + 1,
                           ct.path || '_' || c.id
                    FROM sklad_logic_categories c
                    JOIN cat_tree ct ON c.parent_id = ct.id
                )
                SELECT id, name, level FROM cat_tree ORDER BY path
            """)
            rows = cursor.fetchall()
        self.fields["category"].choices = [
            ("", "—")] + [(r[0], "— " * r[2] + r[1]) for r in rows
        ]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': 'Например: Напитки, Электроника, Одежда'
            }),
        }
        labels = {
            'name': 'Название категории',
            'parent': 'Родительская категория',
        }
        help_texts = {
            'name': 'Основное наименование категории',
            'parent': 'Оставьте пустым, если это корневая категория (верхнего уровня)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].widget = forms.Select(attrs={
            'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors',
        })
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE cat_tree AS (
                    SELECT id, name, parent_id, 0 AS level, CAST(id AS TEXT) AS path
                    FROM sklad_logic_categories WHERE parent_id IS NULL
                    UNION ALL
                    SELECT c.id, c.name, c.parent_id, ct.level + 1,
                           ct.path || '_' || c.id
                    FROM sklad_logic_categories c
                    JOIN cat_tree ct ON c.parent_id = ct.id
                )
                SELECT id, name, level FROM cat_tree ORDER BY path
            """)
            rows = cursor.fetchall()
        self.fields["parent"].choices = [
            ("", "— (корневая)")] + [(r[0], "— " * r[2] + r[1]) for r in rows
        ]


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouses
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': 'Основной склад'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': 'г. Минск, ул. Складская, 1'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': '1000'
            }),
        }
        labels = {
            'name': 'Название склада',
            'address': 'Адрес',
            'capacity': 'Вместимость',
        }


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Suppliers
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': 'ООО "Поставщик"'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': '+375291234567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': 'supplier@example.com'
            }),
        }
        labels = {
            'name': 'Наименование поставщика',
            'contact_phone': 'Контактный телефон',
            'email': 'Email',
        }