from django.db import models


status_choices = (
    ('v', 'Visible'),
    ('h', 'Hidden')
)


class Client(models.Model):
    first_name = models.CharField(u'Имя', max_length=255)
    last_name = models.CharField(u'Фамилия', max_length=255)
    phone = models.CharField('Телефон', unique=True, max_length=12)
    products = models.ManyToManyField('Product', blank=True)

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Product(models.Model):
    name = models.CharField(u'Название', max_length=255)
    author = models.CharField(u'Автор', max_length=255)
    supplier = models.ForeignKey('Supplier', verbose_name='Поставщик', on_delete=models.DO_NOTHING)
    price = models.FloatField("Цена")
    count = models.IntegerField('Кол-во')
    code = models.CharField(u'Адрес ячейки', max_length=5)

    def __str__(self):
        return '{}'.format(self.name)


class Supplier(models.Model):
    name = models.CharField('Имя', max_length=255)
    phone = models.CharField('Телефон', max_length=12)
    address = models.CharField('Адрес', max_length=255)

    def __str__(self):
        return '{!r}'.format(self.name)


class Sale(models.Model):
    date = models.DateField('Дата продажи', auto_now_add=True)
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.DO_NOTHING)
    client = models.ForeignKey(Client, verbose_name='Клиент', on_delete=models.DO_NOTHING)
    count = models.IntegerField('Кол-во')
    sum = models.FloatField('Сумма')

    def __str__(self):
        return '{}'.format(self.pk)
