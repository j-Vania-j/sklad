from django import forms
from .models import Products, Categories


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
            'category': forms.Select(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors'
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


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink placeholder-ash outline-none focus:border-slate-ink transition-colors',
                'placeholder': 'Например: Напитки, Электроника, Одежда'
            }),
            'parent': forms.Select(attrs={
                'class': 'w-full px-12 py-8 bg-transparent border border-dew rounded-chips text-slate-ink outline-none focus:border-slate-ink transition-colors',
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