from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType


fs = FileSystemStorage()


class Product(models.Model):
    """"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    visible = models.BooleanField(default=False)
    added_on = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
    )
    thumbnail = models.ImageField(storage=fs)
    main_image = models.ImageField(storage=fs)

    def __str__(self):
        return self.name

    def _thumb(self):
        return '<img width="100" src="/media/%s">' % self.thumbnail
    _thumb.allow_tags = True

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        thumb_storage, thumb_path = self.thumbnail.storage, self.thumbnail.path
        image_storage = self.main_image.storage
        image_path = self.main_image.path

        # Delete the model before the file
        super(Product, self).delete(*args, **kwargs)
        # Delete the file after the model
        thumb_storage.delete(thumb_path)
        image_storage.delete(image_path)


class Category(models.Model):
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=100, default='all')
    main_image = models.ImageField(storage=fs, default='/media/hat.jpg')

    def __str__(self):
        return self.category


class Image(models.Model):
    image = models.ImageField(storage=fs)
    description = models.TextField()
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
    )

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage, path = self.image.storage, self.image.path
        # Delete the model before the file
        super(Image, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)

    def _img(self):
        return '<img width="300" src="/media/%s">' % self.image
    _img.allow_tags = True


class ChatHistory(models.Model):
    origin = models.CharField(max_length=30)
    to = models.CharField(max_length=30)
    message = models.TextField()

class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    # will make sense with more than one address:
    default = models.BooleanField(default=True)

    number_street = models.CharField(max_length=92)
    suburb = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    region = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    postcode = models.IntegerField()

    def __unicode__(self):
        return self.number_street+' '+self.suburb+', '+self.city+' '+self.region+', '+self.country+' '+str(self.postcode)


class SalesOrder(models.Model):
    buyer = models.ForeignKey(User)
    address = models.ForeignKey(Address)
    created_on = models.DateTimeField(default=timezone.now)

    STATUSES = (
        ('new', 'New Order'),
        ('shipped', 'Order Shipped'),
        ('completed', 'Order Completed'),
        ('cancelled', 'Order Cancelled'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default='new')


class OrderItem(models.Model):
    order = models.ForeignKey(SalesOrder)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    # product as generic relation
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    def __unicode__(self):
        return u'%d units of %s' % (self.quantity, self.product.__class__.__name__)

    def total_price(self):
        return self.quantity * self.unit_price
    total_price = property(total_price)

    # product
    def get_product(self):
        return self.content_type.get_object_for_this_type(pk=self.object_id)

    def set_product(self, product):
        self.content_type = ContentType.objects.get_for_model(type(product))
        self.object_id = product.pk

    product = property(get_product, set_product)


class WishList(models.Model):
    user = models.ForeignKey(User)


class WishListItem(models.Model):
    wishlist = models.ForeignKey(WishList)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()

    def __unicode__(self):
        return self.product.__class__.__name__

    def get_product(self):
        return self.content_type.get_object_for_this_type(pk=self.object_id)

    def set_product(self, product):
        self.content_type = ContentType.objects.get_for_model(type(product))
        self.object_id = product.pk

    product = property(get_product, set_product)

class Contact(models.Model):
	subject = models.CharField(required=True)
	types = (
				('refunds', 'Refund and Cancellation'),
				('missing', 'Where is my stuff?'),
				('violation', 'Report violation of Terms of Service'),
				('phishing', 'Report a phishing incident'),
			)
	message_type = models.CharField(
		max_length=20,
        choices=types,
        default='refunds')
	message = models.TextField()
	email = models.EmailField()
