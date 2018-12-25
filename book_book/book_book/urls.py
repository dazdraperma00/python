"""book_book URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from book_book import views


urlpatterns = [
    path('', views.main),
    path('clients/', views.show_clients),
    path('clients/<int:pk>', views.ClientView.as_view()),
    path('clients/<int:pk>/edit', views.ClientUpdate.as_view()),
    path('clients/add_client/', views.ClientCreate.as_view()),

    path('products/', views.show_products),
    path('products/<int:pk>', views.ProductView.as_view()),
    path('products/<int:pk>/edit', views.ProductUpdate.as_view()),
    path('products/add_product/', views.ProductCreate.as_view()),

    path('suppliers/', views.show_suppliers),
    path('suppliers/<int:pk>', views.SupplierView.as_view()),
    path('suppliers/<int:pk>/edit', views.SupplierUpdate.as_view()),
    path('suppliers/add_supplier/', views.SupplierCreate.as_view()),

    path('sales/', views.show_sales),
    path('sales/add_sale', views.SaleCreate.as_view()),
    path('sales/edit_<int:pk>', views.SaleUpdate.as_view()),

    path('staff/', views.show_staff),
    path('staff/<int:pk>', views.StaffView.as_view()),
    path('staff/<int:pk>/edit', views.StaffUpdate.as_view()),
    path('staff/add_staff/', views.StaffCreate.as_view()),

    path('admin/', admin.site.urls),
]
