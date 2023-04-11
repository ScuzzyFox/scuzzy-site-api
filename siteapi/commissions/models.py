from django.db import models
import os
import uuid
from PIL import Image
# Create your models here.


class CommissionCategory(models.Model):
    name = models.CharField(max_length=100)


class CommissionOption(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField()
    cost = models.DecimalField(decimal_places=2, max_digits=6)
    nsfw = models.BooleanField(default=False)
    abdl = models.BooleanField(default=False)
    exclusive_with = models.CharField(max_length=100)
    required = models.CharField(max_length=100)


class Commission(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, db_index=True, unique=True)
    short_description = models.CharField(max_length=500)
    verbose_description = models.TextField()
    nsfw = models.BooleanField(default=False)
    abdl = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    order_count = models.IntegerField(default=0)
    available = models.BooleanField(default=False)
    ad_blurb = models.TextField()
    categories = models.ManyToManyField(CommissionCategory)
    options = models.ManyToManyField(CommissionOption)

    def toggle_availability(self):
        self.available = not self.available
        self.save()

    def increment_view_count(self):
        self.view_count = self.view_count + 1
        self.save()

    def increment_order_count(self):
        self.order_count = self.order_count + 1
        self.save()


class CommissionVisual(models.Model):
    # eventually want this model to create thumbnail images of
    def get_file_path(instance, filename):

        # extract the extension from the filename
        ext = filename.split('.')[-1]

        # replace filename with a random uuid +.ext
        filename = "%s.%s" % (uuid.uuid4(), ext)

        # combine fileame to path
        return os.path.join('commissions/files/', filename)

    def get_uuid():
        return str(uuid.uuid4())

    def make_thumbnails(self):
        file = self.visual
        group = self.group_identifier
        # Image is coming from from PIL import Image
        im = Image.open(file.path)
        # check for largest dimension
        # save thumbnails in smaller and smaller increments, minimum size being 256px
        # if largest dimension is 2560px, then make thumbnails of 256, 512, 1024, 2048px
        # if largest dimension is 1280px, then make thumbnails of 256, 512, 1024px
        # if largest dimension is 200px, then don't make any thumbnails
        # all of the files will have the same group_identifier as the original
        # all of the files will be webp
        # the above actions should only be done IF the image is a png or jpg

    def delete_group(self):
        # delete all files and db entries of a specific group.
        commissionsInGroup = self.objects.filter(
            group_identifier=self.group_identifier)

        # for each commmission in commissionsInGroup, delete coressponding .visual.path using os.remove

        # once done, call commissionsInGroup.delete()

    commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, related_name='commission_visuals')
    visual = models.FileField(upload_to=get_file_path, max_length=250)
    nsfw = models.BooleanField(default=False)
    abdl = models.BooleanField(default=False)
    is_video = models.BooleanField()
    group_identifier = models.CharField(max_length=100, default=get_uuid)


class CommissionStatus(models.Model):
    status = models.CharField(max_length=100)
    color = models.CharField(max_length=100)

# add order and reference models
