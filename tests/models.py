from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Article(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    date_unique = models.DateTimeField(unique=True)

    def __str__(self):
        return self.title
