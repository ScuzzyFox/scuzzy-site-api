from .models import Goal
from rest_framework import serializers
from django.utils.text import slugify


class GoalSerializer(serializers.ModelSerializer):
    """Used for Create, Update, Delete actions"""
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
            "image": {"write_only": True}

        }

    def get_image_url(self, object):
        request = self.context.get('request')
        object_url = object.image.url
        return request.build_absolute_uri(object_url)

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"].lower())
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        validated_data["slug"] = slugify(validated_data["name"].lower())
        return super().update(instance, validated_data=validated_data)
