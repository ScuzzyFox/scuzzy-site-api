from .models import Commission, CommissionCategory, CommissionOption, CommissionOrder, CommissionStatus, CommissionVisual, CharacterReference
from rest_framework import serializers
from django.utils.text import slugify


class CommissionVisualSerializer(serializers.ModelSerializer):
    # commission id is provided to relate a visual to a commission
    visual_url = serializers.SerializerMethodField()
    commission = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = CommissionVisual
        fields = [
            'id',
            'visual',
            'adult',
            'abdl',
            'visual_url',
            'is_video',
            'group_identifier',
            'order',
            'commission'
        ]

        extra_kwargs = {
            'visual': {"write_only": True},
            'visual_url': {"read_only": True}
        }

    def get_visual_url(self, obj):
        request = self.context.get('request')
        object_url = obj.visual.url
        return request.build_absolute_uri(object_url).replace('http://', 'https://')

    def create(self, validated_data):
        instance = super().create(validated_data)
        try:
            instance.rename_file_with_uuid()

        except Exception as e:
            print(e)
            instance.delete()
            raise serializers.ValidationError(
                "Something went wrong. Could not rename file.")
        try:

            instance.convert_to_webp()
        except Exception as e:
            print(e)
            instance.delete()
            raise serializers.ValidationError(
                "Something went wrong. Could not convert to webp.")
        try:
            instance.remove_all_files_not_attached_to_model()
        except Exception as e:
            print(e)
            instance.delete()
            raise serializers.ValidationError(
                "Something went wrong. Could not remove files not attached to model.")
        try:
            instance.generate_thumbnails()
        except Exception as e:
            print(e)
            instance.delete()
            raise serializers.ValidationError(
                "Something went wrong. Could not generate thumbnails.")

        return instance


class CommissionOptionSerializer(serializers.ModelSerializer):
    example_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CommissionOption
        fields = [
            'id',
            'name',
            'description',
            'cost',
            'adult',
            'abdl',
            'exclusive_with',
            'required',
            'example_image',
            'example_image_url'
        ]

        extra_kwargs = {
            'example_image': {"write_only": True}
        }

    def get_example_image_url(self, obj):
        request = self.context.get('request')
        object_url = obj.example_image.url
        return request.build_absolute_uri(object_url).replace('http://', 'https://')


class CommissionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionCategory
        fields = [
            'id',
            'name',
            'adult',
            'abdl'
        ]


class CommissionSerializer(serializers.ModelSerializer):
    options = CommissionOptionSerializer(many=True, read_only=True)
    visuals = CommissionVisualSerializer(many=True, read_only=True)
    categories = CommissionCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Commission
        fields = [
            'id',
            'title',
            'slug'
            'short_description',
            'verbose_description',
            'adult',
            'abdl',
            'created',
            'modified',
            'view_count',
            'order_count',
            'available',
            'ad_blurb',
            'should_be_featured',
            'options',
            'visuals',
            'visible',
            'categories'
        ]
        extra_kwargs = {
            "options": {"read_only": True},
            "visuals": {"read_only": True},
            "categories": {"read_only": True},
            "slug": {"read_only": False}
        }

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['title'])
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        # if title was provided, then update slug
        if validated_data.get('title'):
            validated_data['slug'] = slugify(validated_data['title'])
        return super().update(instance, validated_data=validated_data)

# --------------^^^^^^ COMMISSIONS ^^^^^^^---------------


# --------------vvvvv ORDERS vvvvvv----------------

class CommissionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionStatus
        fields = [
            'id',
            'status',
            'color',
        ]


class CharacterReferenceSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CharacterReference
        fields = [
            'id',
            'character_name',
            'order',
            'link',
            'image',
            'image_url',
            'adult',
            'abdl',
        ]

        extra_kwargs = {
            'image': {"write_only": True, "required": False},
            'image_url': {"read_only": True},
            "link": {"required": False}
        }

    def get_image_url(self, obj):
        # should probably check if image exists first. if not then return null
        request = self.context.get('request')
        object_url = obj.image.url
        if not object_url:
            return None
        return request.build_absolute_uri(object_url).replace('http://', 'https://')


class CommissionOrderSerializer(serializers.ModelSerializer):
    statuses = CommissionStatusSerializer(read_only=True,  many=True)
    character_references = CharacterReferenceSerializer(
        read_only=True,  many=True)
    commission = serializers.PrimaryKeyRelatedField()
    selected_options = CommissionOptionSerializer(read_only=True,  many=True)

    class Meta:
        model = CommissionOrder
        fields = [
            'id',
            'commission',
            'subtotal',
            'selected_options',
            'statuses',
            'customer_name',
            'where_to_contact',
            'contact_info',
            'email',
            'abdl',
            'adult',
            'created',
            'modified',
            'artist_note',
            'extra_character_details',
            'commission_description',
            'number_of_characters',
            'customer_sketch',
            'character_references',
            'completed'
        ]
        extra_kwargs = {
            "selected_options": {"read_only": True},
            "statuses": {"read_only": True},
            "character_references": {"read_only": True}
        }

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.calculate_subtotal()
