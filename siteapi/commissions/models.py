import decimal
from django.db import models
import os
import uuid
from PIL import Image


class CommissionCategory(models.Model):
    # done
    name = models.CharField(max_length=100)
    abdl = models.BooleanField(default=False)
    adult = models.BooleanField(default=False)


class CommissionOption(models.Model):
    # done?
    name = models.CharField(max_length=250)
    description = models.TextField()
    cost = models.DecimalField(decimal_places=2, max_digits=6)
    adult = models.BooleanField(default=False)
    abdl = models.BooleanField(default=False)
    # an order can't contain more than one option with the same exclusive_with property
    exclusive_with = models.CharField(max_length=100, blank=True, null=True)

    # an order needs 1 or more of each unique required
    required = models.CharField(max_length=100, blank=True, null=True)
    example_image = models.ImageField(blank=True)

    class Meta:
        # ascending by name
        ordering = ['name', 'id']

    def get_other_required(self):
        return CommissionOption.objects.filter(required=self.required)

    def get_exclusive_with(self):
        return CommissionOption.objects.filter(exclusive_with=self.exclusive_with)


class Commission(models.Model):
    # done
    def get_file_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join('commissions/ads/', filename)

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, db_index=True,
                            unique=True, blank=True, null=True)
    short_description = models.CharField(max_length=500)
    verbose_description = models.TextField()  # markdown or html?
    adult = models.BooleanField(default=False)
    abdl = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    order_count = models.IntegerField(default=0)
    available = models.BooleanField(default=False)
    ad_blurb = models.TextField()
    ad_image = models.ImageField(upload_to=get_file_path, blank=True)
    categories = models.ManyToManyField(CommissionCategory)
    options = models.ManyToManyField(CommissionOption)
    # should this show as a front page item?
    should_be_featured = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    base_price = models.IntegerField(default=0)

    def toggle_featured(self):
        self.should_be_featured = not self.should_be_featured
        self.save()

    def toggle_visibility(self):
        self.visible = not self.visible
        self.save()

    def toggle_availability(self):
        self.available = not self.available
        self.save()

    def increment_view_count(self):
        self.view_count = self.view_count + 1
        self.save()

    def calculate_order_count(self):
        self.order_count = CommissionOrder.objects.filter(
            commission_id=self.id).filter(completed=True).count()
        self.save()


class CommissionVisual(models.Model):
    # done
    def get_uuid():
        return str(uuid.uuid4())

    commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, related_name='commission_visuals')
    # visual could be a video, gif, or an image
    visual = models.FileField(upload_to='commissions/visuals/', max_length=250)
    adult = models.BooleanField(default=False)
    abdl = models.BooleanField(default=False)
    is_video = models.BooleanField(default=False)
    group_identifier = models.CharField(max_length=100, default=get_uuid)
    order = models.IntegerField()

    # default order should be by order ascending:
    class Meta:
        ordering = ['order']

    def rename_file_with_uuid(self):
        # doesn't matter what file type it is, just rename it with a uuid
        # using this instead of upload_to callable since it seems to interfere with the image.save() part of making thumbnails
        # generate the uuid
        uid = uuid.uuid4()
        # get the file_field
        file = self.visual
        # get the file extension
        ext = os.path.splitext(file.name)[1]
        # get the original file name
        OG_name = os.path.basename(file.path)
        # rename the file physically on the disk to same location with modified name
        os.rename(file.path, file.path.replace(OG_name, str(uid)+ext))
        # set the new file to the file_field (this part only changes the path represented as text in the database)
        self.visual = file.name.replace(OG_name, str(uid)+ext)
        # save the model
        self.save()

    def convert_to_webp(self):
        # if file_field is a png or jpeg, then convert it to webp using pillow, ensuring to delete the old file.
        # if file_field is anything else, then do nothing.

        # brings up a FieldFile object from the model (which is like a file object)
        file = self.visual
        if file.name.endswith('.png') or file.name.endswith('.jpeg') or file.name.endswith('.jpg'):
            print("----CONVERTING TO WEBP-----")
            # open the file (with makes sure to close the resource after the operation is complete)
            with Image.open(file) as image:
                # save the file as a webp physically on the disk to the original path (with extension replaced)
                image.save(file.path.replace('.png', '.webp').replace(
                    '.jpeg', '.webp').replace('.jpg', '.webp'), format='WEBP')
                # set the new file to the file_field (this part only changes the path represented as text in the database)
                self.visual = file.name.replace('.png', '.webp').replace(
                    '.jpeg', '.webp').replace('.jpg', '.webp')
                # save the model
                self.save()
                # probably not needed but i'm not smart enough to know
                image.close()
                file.close()
        self.remove_all_files_not_attached_to_model()

    def generate_thumbnails(self):
        def generate_sizes(max):
            sizes = []
            i = 256
            while i < max:
                sizes.append(i)
                i = i * 2
            # return sizes reversed
            return sizes[::-1]
        file = self.visual
        ext = os.path.splitext(file.name)[1]
        # OG_name = os.path.splitext(file)[0]
        if str(ext).lower() in ['.png', '.jpeg', '.jpg', '.webp']:
            print(file.path)
            with Image.open(file.path) as image:
                (x, y) = image.size
                largest = x if x > y else y
                sizes = generate_sizes(largest)
                for s in sizes:
                    # create a new file object with the new path
                    new_file = file.path.replace(ext, '_'+str(s)+ext)
                    # make sure this file doesn't already exist
                    if os.path.exists(new_file):
                        continue
                    # resize the image
                    image.thumbnail((s, s))
                    # save the file physically on the disk to same location with modified name
                    image.save(new_file)
                    # set the new file to the file_field (this part only changes the path represented as text in the database)
                    # have to use name here and not path because path is the full path to the file on the disk, and name is just the relative location of the file compared to MEDIA_ROOT
                    new_model = CommissionVisual(
                        group_identifier=self.group_identifier, visual=file.name.replace(ext, '_'+str(s)+ext), commission=self.commission, adult=self.adult, abdl=self.abdl, is_video=self.is_video, order=self.order)
                    # new_model.visual = file.name.replace(ext, '_'+str(s)+ext)
                    # save the model
                    new_model.save()

    def remove_all_files_not_attached_to_model(self):
        # delete all files not attached to any models
        # get directory of a file_field (might want to upgrade this and use the MEDIA_ROOT variable)
        directory = os.path.dirname(self.visual.path)
        all_files_in_directory = []

        # put all the files in the directory in a list
        for file in os.listdir(directory):
            all_files_in_directory.append(file)
        # get every model instance that exists
        all_instances = CommissionVisual.objects.all()
        filenames = []
        # put every model instance's file_field basename in a list
        for instance in all_instances:
            filenames.append(os.path.basename(instance.visual.path))

        # for each file in the directory, check if it's in the list of model instances' file_field basenames. If not, then delete it.
        for file in all_files_in_directory:
            if file not in filenames:
                try:
                    os.remove(os.path.join(directory, file))
                except Exception as e:
                    print(e)
                    print("Could not remove "+str(file))

    def delete(self, *args, **kwargs):
        # delete the file
        try:
            os.remove(self.visual.path)
            self.remove_all_files_not_attached_to_model()
        except:
            pass
        # delete the model
        super().delete(*args, **kwargs)
        try:
            os.remove(self.visual.path)
            self.remove_all_files_not_attached_to_model()
        except:
            pass

    def delete_group(self):
        # delete all files and db entries of a specific group.
        commissionsInGroup = self.objects.filter(
            group_identifier=self.group_identifier)
        # for each commmission in commissionsInGroup, delete coressponding .visual.path using os.remove, if the file exists
        for commission in commissionsInGroup:
            try:
                commission.delete()
            except:
                print("Could not delete commission instance")
        self.remove_all_files_not_attached_to_model()


class CommissionStatus(models.Model):
    # done
    status = models.CharField(max_length=100)
    # hex code string for css
    color = models.CharField(max_length=100)


class CommissionOrder(models.Model):
    # done
    commission = models.ForeignKey(
        Commission, on_delete=models.CASCADE, related_name='order')
    subtotal = models.DecimalField(
        decimal_places=2, max_digits=6, default=0.00)
    selected_options = models.ManyToManyField(CommissionOption)
    statuses = models.ManyToManyField(CommissionStatus)
    customer_name = models.CharField(max_length=250)
    # where to contact is a list of choices. choices are telegram, discord, twitter, or furaffinity
    TELEGRAM = "TG"
    DISCORD = "DC"
    TWITTER = "TW"
    FURAFFINITY = "FA"
    CONTACT_CHOICES = [
        (TELEGRAM, "Telegram"),
        (DISCORD, "Discord"),
        (TWITTER, "Twitter"),
        (FURAFFINITY, "FurAffinity"),
    ]
    where_to_contact = models.CharField(
        max_length=2, choices=CONTACT_CHOICES)
    contact_info = models.CharField(max_length=250)
    email = models.EmailField()
    abdl = models.BooleanField()
    adult = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    artist_note = models.TextField(blank=True, null=True)
    extra_character_details = models.TextField(blank=True, null=True)
    commission_description = models.TextField()
    number_of_characters = models.IntegerField()
    # this is a data url of customer's sketch.
    customer_sketch = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def calculate_subtotal(self):
        CHARACTER_MODIFIER = decimal.Decimal(0.45)
        # query all of the commission options belonging to the order.
        opts = self.selected_options.all() if self.selected_options.all() else None
        print(opts)
        # sum all of the costs of each commission option.
        sum = 0
        if opts is not None:
            for opt in opts:
                sum += opt.cost
        # assign the sum to the subtotal property
        self.subtotal = sum + self.commission.base_price + \
            (self.number_of_characters-1) * CHARACTER_MODIFIER * \
            (sum + self.commission.base_price)
        # save the model
        self.save()

    def save(self, *args, **kwargs):
        # save the model
        super().save(*args, **kwargs)
        self.commission.calculate_order_count()

    def toggle_completed(self):
        self.completed = not self.completed
        self.save()


class CharacterReference(models.Model):
    # done
    def get_file_path(instance, filename):
        # extract the extension from the filename
        ext = filename.split('.')[-1]
        # replace filename with a random uuid +.ext
        filename = "%s.%s" % (uuid.uuid4(), ext)
        # combine fileame to path
        return os.path.join('goals/images/', filename)

    character_name = models.CharField(max_length=250)
    order = models.ForeignKey(
        CommissionOrder, on_delete=models.CASCADE, related_name='character_references')
    # link OR image allowed, not both.
    link = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path,  blank=True, null=True)
    text_description = models.TextField(blank=True, null=True)
    adult = models.BooleanField()
    abdl = models.BooleanField()

    # add a constraint to ensure that at least one link or image is provided, but not both.
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(link__isnull=False, image__isnull=False) | models.Q(
                    link__isnull=True, image__isnull=True),
                name='link_or_image_required'
            )
        ]

    def delete(self, *args, **kwargs):
        # delete the image
        try:
            os.remove(self.image.path)
        except:
            pass
        # delete the model
        super().delete(*args, **kwargs)
        try:
            os.remove(self.image.path)
        except:
            pass
