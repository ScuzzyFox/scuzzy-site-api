from .models import Goal
from rest_framework import serializers
from django.utils.text import slugify


class GoalSerializer(serializers.ModelSerializer):
    """
    Serializer class for creating, updating and deleting a Goal instance. Returns a serialized version of the model
    that includes an `image_url` property with an absolute URL to the image file. The `image_url` is generated using
    the `get_image_url()` method, which uses the `request` object to build an absolute URI to the image file.
    """

    # image_url is a property that is tied to the return of a mehtod. in this case the default is get_image_url
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = '__all__'
        extra_kwargs = {
            "created": {"required": False},
            "fulfilled": {"required": False},
            "date_fulfilled": {"required": False},
            "use_case": {"required": False},
            "slug": {"required": False},

            # prevent image property from being returned
            "image": {"write_only": True}

        }

    def get_image_url(self, object):
        """
     Returns the absolute URL of the goal image.

     Args:
         object (Goal): The instance of the goal being serialized.

     Returns:
         str: The absolute URL of the image associated with the goal in https.

     """
        request = self.context.get('request')
        object_url = object.image.url

        # Replace http with https in the image URL.
        # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        # &
        # USE_X_FORWARDED_HOST = True
        # in settings would get around this, but I don't mind doing this for now.
        # this is a result of using nginx as a reverse proxy.
        return request.build_absolute_uri(object_url).replace('http://', 'https://')

    def create(self, validated_data):
        """
        Creates a new instance of the Goal model with the validated data and sets its slug based on its name.

        Args:
            validated_data (dict): The validated data to create the instance.

        Returns:
            Goal: The newly created instance.
        """
        validated_data["slug"] = slugify(validated_data["name"].lower())
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        """
        Updates an existing instance of the Goal model with the validated data and updates its slug based on its name.

        Args:
            instance (Goal): The instance to update.
            validated_data (dict): The validated data to update the instance.

        Returns:
            Goal: The updated instance.
        """
        validated_data["slug"] = slugify(validated_data["name"].lower())
        return super().update(instance, validated_data=validated_data)
