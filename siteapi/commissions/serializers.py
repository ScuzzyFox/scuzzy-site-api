import traceback
from .models import Commission, CommissionCategory, CommissionOption, CommissionOrder, CommissionStatus, CommissionVisual, CharacterReference
from rest_framework import serializers
from django.utils.text import slugify


class CommissionVisualSerializer(serializers.ModelSerializer):
    # commission id is provided to relate a visual to a commission
    visual_url = serializers.SerializerMethodField()
    commission = serializers.PrimaryKeyRelatedField(
        queryset=Commission.objects.all())

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
            print(traceback.format_exc())
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
            'example_image': {"write_only": True, "required": False},
            'example_image_url': {"required": False}
        }

    def get_example_image_url(self, obj):
        request = self.context.get('request')
        try:
            object_url = obj.example_image.url
        except:
            object_url = None
        if object_url is not None:
            return request.build_absolute_uri(object_url).replace('http://', 'https://')
        return None


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
    commission_visuals = CommissionVisualSerializer(many=True, read_only=True)
    categories = CommissionCategorySerializer(many=True, read_only=True)
    ad_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Commission
        fields = [
            'id',
            'title',
            'slug',
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
            'commission_visuals',
            'visible',
            'categories',
            'ad_image',
            'ad_image_url',
            'base_price',
        ]
        extra_kwargs = {
            "options": {"read_only": True},
            "commission_visuals": {"read_only": True},
            "categories": {"read_only": True},
            "slug": {"read_only": False},
            "ad_image_url": {"read_only": True},
            "ad_image": {"write_only": True, "required": False}
        }

    def get_ad_image_url(self, obj):
        request = self.context.get('request')
        try:
            object_url = obj.ad_image.url
        except:
            object_url = None
        if object_url is not None:
            return request.build_absolute_uri(object_url).replace('http://', 'https://')
        return None

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['title'])
        instance = super().create(validated_data=validated_data)
        instance.calculate_order_count()
        return instance

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
    order = serializers.PrimaryKeyRelatedField(
        queryset=CommissionOrder.objects.all())
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
            'text_description',
        ]

        extra_kwargs = {
            'image': {"write_only": True, "required": False},
            'image_url': {"read_only": True},
            "link": {"required": False},
            'text_description': {"required": False}
        }

    def get_image_url(self, obj):
        request = self.context.get('request')
        try:
            object_url = obj.image.url
        except:
            object_url = None
        if object_url is not None:
            return request.build_absolute_uri(object_url).replace('http://', 'https://')
        return None


class CommissionOrderSerializer(serializers.ModelSerializer):
    statuses = CommissionStatusSerializer(read_only=True,  many=True)
    character_references = CharacterReferenceSerializer(
        read_only=True,  many=True)
    commission = serializers.PrimaryKeyRelatedField(queryset=Commission.objects.all())
    commission_data = CommissionSerializer(read_only=True)
    selected_options = CommissionOptionSerializer(read_only=True,  many=True)

    class Meta:
        model = CommissionOrder
        fields = [
            'id',
            'commission',
            'commission_data',
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
        instance.commission.calculate_order_count()
        return instance

    def create(self, validated_data):
        instance = super().create(validated_data=validated_data)
        instance.commission.calculate_order_count()
        return instance

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        instance.commission.calculate_order_count()
        return instance


class AnonymousCharacterReferenceSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(
        queryset=CommissionOrder.objects.all())

    class Meta:
        model = CharacterReference
        fields = [
            'id',
            'character_name',
            'order',
            'adult',
            'abdl',
        ]


class AnonymousOrderSerializer(serializers.ModelSerializer):
    statuses = CommissionStatusSerializer(read_only=True,  many=True)
    character_references = AnonymousCharacterReferenceSerializer(
        read_only=True, many=True)

    class Meta:
        model = CommissionOrder
        fields = [
            'id',
            'customer_name',
            'adult',
            'abdl',
            'statuses',
            'created',
            'modified',
            'artist_note',
            'completed',
            'character_references'
        ]
