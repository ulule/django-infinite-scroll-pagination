import uuid

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Article(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    date_unique = models.DateTimeField(unique=True)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class ArticleCustomPK(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    date = models.DateTimeField()

    def __str__(self):
        return self.title
