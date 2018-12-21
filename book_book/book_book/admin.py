from book_book import models
from django.contrib import admin


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'phone', 'address')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'phone')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'price', 'count', 'supplier', 'code')


class SaleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'client', 'count', 'sum', 'date')


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Supplier, SupplierAdmin)
admin.site.register(models.Sale, SaleAdmin)
