from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class TaggedItemManager(models.Manager):
    def get_tags_for(self, object_type, object_id):
        # Find the content type id for the product model
        content_type = ContentType.objects.get_for_model(object_type)
        return TaggedItem.objects.select_related('tag').filter(content_type=content_type, object_id=object_id)


# Create your models here.
class Tag(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label


class TaggedItem(models.Model):
    objects = TaggedItemManager()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return self.tag.label