from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Max, Min, Sum

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from book_book.models import Client, Product, Supplier, Sale, Staffer


def set_path(path, context):

    if path == '/':
        context['back'] = ''
        return

    idx = path[:-1].rindex('/')

    context['back'] = path[:idx + 1]



def main(request):

    products = Product.objects
    clients = Client.objects
    suppliers = Supplier.objects
    sales = Sale.objects
    staff = Staffer.objects

    context = {
        'products': products.count(),
        'clients': clients.count(),
        'suppliers': suppliers.count,
        'staff': staff.count(),
        'sales': sales.count()
    }
    return render(request, 'main.html', context)


def show_clients(request):
    name = request.GET.get('text', '')

    context = {'client_add_url': 'add_client'}

    clients = Client.objects.filter(last_name__contains=name)

    context['clients'] = clients

    s = Sale.objects

    unique_clients = s.values('client').distinct()

    list_of_id = []
    for obj in unique_clients:
        client_id = obj['client']
        list_of_id.append(client_id)

    total_sum = {}
    for cl_id in list_of_id:
        total = s.filter(client__id=cl_id).aggregate(total=Sum('sum'))['total']
        total_sum[total] = cl_id

    best_client_id = total_sum[max(total_sum)]

    best_client = Client.objects.filter(id=best_client_id)

    context['best_client'] = best_client[0]

    set_path(request.path, context)

    return render(request, 'clients.html', context)


class ClientView(DetailView):
    model = Client
    template_name = 'client_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client = context['client']

        context['edit_client'] = '{}/edit'.format(client.pk)

        set_path(self.request.path, context)

        return context


class ClientCreate(CreateView):
    model = Client
    fields = ['first_name', 'last_name', 'phone', 'email']
    template_name = 'create_client.html'

    def get_success_url(self):
        return "/clients/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context


class ClientUpdate(UpdateView):
    model = Client
    fields = ['first_name', 'last_name', 'phone', 'email']
    template_name = 'edit_client.html'

    def get_success_url(self):
        return "/clients/{}".format(self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context


def show_products(request):
    name = request.GET.get('text', '')

    context = {'product_add_url': 'add_product'}

    products = Product.objects.filter(name__contains=name)

    context['products'] = products

    max_price = products.aggregate(max_price=Max('price'))['max_price']
    min_price = products.aggregate(min_price=Min('price'))['min_price']

    context['costly'] = products.filter(price=max_price)[0].name
    context['cheap'] = products.filter(price=min_price)[0].name

    set_path(request.path, context)

    return render(request, 'products.html', context)


class ProductView(DetailView):
    model = Product
    template_name = 'product_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = context['product']

        context['edit_product'] = '{}/edit'.format(product.pk)

        set_path(self.request.path, context)

        return context


class ProductCreate(CreateView):
    model = Product
    fields = ['name', 'author', 'supplier', 'price', 'count', 'code']
    template_name = 'create_product.html'

    def get_success_url(self):
        return "/products/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context


class ProductUpdate(UpdateView):
    model = Product
    fields = ['name', 'author', 'supplier', 'price', 'count', 'code']
    template_name = 'edit_product.html'

    def get_success_url(self):
        return "/products/{}".format(self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context


def show_suppliers(request):
    name = request.GET.get('text', '')

    context = {'supplier_add_url': 'add_supplier'}

    suppliers = Supplier.objects.filter(name__contains=name)

    context['suppliers'] = suppliers

    set_path(request.path, context)

    return render(request, 'suppliers.html', context)


class SupplierView(DetailView):
    model = Supplier
    template_name = 'supplier_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        supplier = context['supplier']

        context['edit_supplier'] = '{}/edit'.format(supplier.pk)

        set_path(self.request.path, context)

        return context


class SupplierCreate(CreateView):
    model = Supplier
    fields = ['name', 'phone', 'email', 'address']
    template_name = 'create_supplier.html'

    def get_success_url(self):
        return "/suppliers/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context


class SupplierUpdate(UpdateView):
    model = Supplier
    fields = ['name', 'phone', 'email', 'address']
    template_name = 'edit_supplier.html'

    def get_success_url(self):
        return "/suppliers/{}".format(self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context


def show_sales(request):
    sales = Sale.objects.all()
    context = {'sales': sales}

    context['sale_add_url'] = 'add_sale'

    set_path(request.path, context)

    return render(request, 'sales.html', context)


class SaleCreate(CreateView):
    model = Sale
    fields = ['date', 'product', 'client', 'staffer', 'count', 'sum']
    template_name = 'create_sale.html'

    def get_success_url(self):
        return "/sales/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context


class SaleUpdate(UpdateView):
    model = Sale
    fields = ['date', 'product', 'client', 'staffer', 'count', 'sum']
    template_name = 'edit_sale.html'

    def get_success_url(self):
        return "/sales"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context


def show_staff(request):
    name = request.GET.get('text', '')

    context = {'staff_add_url': 'add_staff'}

    staff = Staffer.objects.filter(last_name__contains=name)

    s = Sale.objects

    unique_staffers = s.values('staffer').distinct()

    list_of_id = []
    for obj in unique_staffers:
        staffer_id = obj['staffer']
        list_of_id.append(staffer_id)

    total_sum = {}
    for cl_id in list_of_id:
        total = s.filter(staffer__id=cl_id).aggregate(total=Sum('sum'))['total']
        total_sum[total] = cl_id

    best_staffer_id = total_sum[max(total_sum)]

    best_staffer = Staffer.objects.filter(id=best_staffer_id)

    context['best_staffer'] = best_staffer[0]

    context['staff'] = staff

    set_path(request.path, context)

    return render(request, 'staff.html', context)


class StaffView(DetailView):
    model = Staffer
    template_name = 'staffer_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        staffer = context['staffer']

        context['edit_staff'] = '{}/edit'.format(staffer.pk)

        set_path(self.request.path, context)

        return context


class StaffCreate(CreateView):
    model = Staffer
    fields = ['first_name', 'last_name', 'phone', 'email', 'post']
    template_name = 'create_staff.html'

    def get_success_url(self):
        return "/staff/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context


class StaffUpdate(UpdateView):
    model = Staffer
    fields = ['first_name', 'last_name', 'phone', 'email', 'post']
    template_name = 'edit_staff.html'

    def get_success_url(self):
        return "/staff/{}".format(self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        set_path(self.request.path, context)

        return context
