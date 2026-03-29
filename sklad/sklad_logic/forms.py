from django import forms
from .models import Products, Categories

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition duration-200',
                'placeholder': 'Например: Coca-Cola 0.5л'
            }),
            'sku': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition duration-200',
                'placeholder': 'Артикул'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition duration-200'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition duration-200',
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
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition duration-200 bg-white text-gray-900 placeholder-gray-400',
                'placeholder': 'Например: Напитки, Электроника, Одежда'
            }),
            'parent': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition duration-200 bg-white text-gray-900',
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