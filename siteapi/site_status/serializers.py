from .models import PageView, SiteStatus
from rest_framework import serializers


class PageViewSerializer(serializers.ModelSerializer):
    site_origin = serializers.SerializerMethodField()

    class Meta:
        model = PageView
        fields = ('site_origin', 'pathname', 'view_count')

    def get_site_origin(self, object):
        return object.site_status.origin


class SiteStatusSerializer(serializers.ModelSerializer):
    page_views = PageViewSerializer(many=True, read_only=True)

    class Meta:
        model = SiteStatus
        fields = ('origin', 'commissions_open', 'requests_open',
                  'art_trades_open', 'store_open', 'website_views', 'page_views')
        extra_kwargs = {
            # remove unique validator from Origin field
            'origin': {'validators': []},
        }
