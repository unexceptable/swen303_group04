from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage


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
