from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Max, Min

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from book_book.models import Client, Product, Supplier, Sale


def main(request):
    products = Product.objects
    clients = Client.objects
    suppliers = Supplier.objects
    sales = Sale.objects

    context = {
        'products': products.count(),
        'clients': clients.count(),
        'suppliers': suppliers.count,
        'sales': sales.count()
    }
    return render(request, 'main.html', context)


def show_clients(request):
    name = request.GET.get('text', '')

    context = {'client_add_url': 'add_client'}

    clients = Client.objects.filter(last_name__contains=name)

    context['clients'] = clients

    return render(request, 'clients.html', context)


class ClientView(DetailView):
    model = Client
    template_name = 'client_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = context['client']

        context['edit_client'] = '{}/edit'.format(client.pk)

        return context


class ClientCreate(CreateView):
    model = Client
    fields = ['first_name', 'last_name', 'phone']
    template_name = 'create_client.html'

    def get_success_url(self):
        return "/clients/"


class ClientUpdate(UpdateView):
    model = Client
    fields = ['first_name', 'last_name', 'phone']
    template_name = 'edit_client.html'

    def get_success_url(self):
        return "/clients/{}".format(self.kwargs['pk'])


def show_products(request):
    name = request.GET.get('text', '')

    context = {'product_add_url': 'add_product'}

    products = Product.objects.filter(name__contains=name)

    context['products'] = products

    max_price = products.aggregate(max_price=Max('price'))['max_price']
    min_price = products.aggregate(min_price=Min('price'))['min_price']

    context['costly'] = products.filter(price=max_price)[0].name
    context['cheap'] = products.filter(price=min_price)[0].name

    return render(request, 'products.html', context)


class ProductView(DetailView):
    model = Product
    template_name = 'product_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = context['product']

        context['edit_product'] = '{}/edit'.format(product.pk)

        return context


class ProductCreate(CreateView):
    model = Product
    fields = ['name', 'author', 'supplier', 'price', 'count', 'code']
    template_name = 'create_product.html'

    def get_success_url(self):
        return "/products/"


class ProductUpdate(UpdateView):
    model = Product
    fields = ['name', 'author', 'supplier', 'price', 'count', 'code']
    template_name = 'edit_product.html'

    def get_success_url(self):
        return "/products/{}".format(self.kwargs['pk'])


def show_suppliers(request):
    name = request.GET.get('text', '')

    context = {'supplier_add_url': 'add_supplier'}

    suppliers = Supplier.objects.filter(name__contains=name)

    context['suppliers'] = suppliers

    return render(request, 'suppliers.html', context)


class SupplierView(DetailView):
    model = Supplier
    template_name = 'supplier_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        supplier = context['supplier']

        context['edit_supplier'] = '{}/edit'.format(supplier.pk)

        return context


class SupplierCreate(CreateView):
    model = Supplier
    fields = ['name', 'phone', 'address']
    template_name = 'create_supplier.html'

    def get_success_url(self):
        return "/suppliers/"


class SupplierUpdate(UpdateView):
    model = Supplier
    fields = ['name', 'phone', 'address']
    template_name = 'edit_supplier.html'

    def get_success_url(self):
        return "/suppliers/{}".format(self.kwargs['pk'])


def show_sales(request):
    sales = Sale.objects.all()
    context = {'sales': sales}

    context['sale_add_url'] = 'add_sale'

    return render(request, 'sales.html', context)


class SaleCreate(CreateView):
    model = Sale
    fields = ['product', 'client', 'count', 'sum']
    template_name = 'create_sale.html'

    def get_success_url(self):
        return "/sales/"
