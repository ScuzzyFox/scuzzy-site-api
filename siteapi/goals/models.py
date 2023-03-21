import os
import uuid

from django.db import models
from django.dispatch import receiver
from django.db import models
from django.utils import timezone


# Create your models here.


class Goal(models.Model):

    def get_file_path(instance, filename):

        # extract the extension from the filename
        ext = filename.split('.')[-1]

        # replace filename with a random uuid +.ext
        filename = "%s.%s" % (uuid.uuid4(), ext)

        # combine fileame to path
        return os.path.join('goals/images/', filename)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    cost = models.DecimalField(decimal_places=2, max_digits=6)
    name = models.CharField(max_length=30, unique=True)
    description = models.TextField("what is it?")
    use_case = models.TextField(
        "why do I need/want and how will I use it?", blank=True, null=True)
    fulfilled = models.BooleanField(default=False)
    date_fulfilled = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(db_index=True, unique=True)
    image = models.ImageField(
        upload_to=get_file_path)
    image_alt = models.CharField(max_length=100)

    def make_fulfilled(self):
        if not self.fulfilled:
            self.fulfilled = True
            self.date_fulfilled = timezone.now()
            self.save()


@receiver(models.signals.post_delete, sender=Goal)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=Goal)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Goal.objects.get(pk=instance.pk).image
    except Goal.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
