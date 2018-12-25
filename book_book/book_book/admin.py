from book_book import models
from django.contrib import admin


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'phone', 'email', 'address')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'phone', 'email')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'price', 'count', 'supplier', 'code')


class SaleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'client', 'staffer', 'count', 'sum', 'date')


class StafferAdmin(admin.ModelAdmin):
    list_display = ('pk', 'first_name', 'last_name', 'phone', 'email', 'post')


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.Supplier, SupplierAdmin)
admin.site.register(models.Sale, SaleAdmin)
admin.site.register(models.Staffer, StafferAdmin)