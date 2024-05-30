from rest_framework import generics, mixins, status
from customAuth.backends import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import PageView, SiteStatus
from .serializers import SiteStatusSerializer, PageViewSerializer
from django.db import models


class ListSiteStatus(generics.ListAPIView):
    """Returns a list of all site statuses"""
    permission_classes = ()
    queryset = SiteStatus.objects.all()
    serializer_class = SiteStatusSerializer


class SiteStatusDetail(APIView):
    """Returns the site status for a specific origin and creates it if it doesn't exist"""
    permission_classes = ()
    serializer_class = SiteStatusSerializer

    def get_site_status(self, origin):
        """Gets the site status object if it exists, else creates a new one"""
        try:
            site_status = SiteStatus.objects.get(origin=origin)
            # calculates total website views based on sum of all page views
            total_web_views = PageView.objects.filter(site_status=site_status).aggregate(
                sum_views=models.Sum('view_count')).get('sum_views', 0)
            site_status.website_views = total_web_views if total_web_views is not None else 0
            site_status.save()
            return site_status
        except SiteStatus.DoesNotExist:
            if "scuzzyfox.com" in str(origin):
                site_status = SiteStatus(origin=origin)
                site_status.save()
                # calculates total website views based on sum of all page views
                total_web_views = PageView.objects.filter(site_status=site_status).aggregate(
                    sum_views=models.Sum('view_count')).get('sum_views', 0)
                site_status.website_views = total_web_views if total_web_views is not None else 0
                site_status.save()
                return site_status

    def get(self, request, origin):

        site_status = self.get_site_status(origin=origin)
        serializer = self.serializer_class(site_status)
        return Response(serializer.data)


class PageViewDetail(APIView):
    """
    Get: returns a specific page view or creates it if it doesn't exist. does not increment.

    Post: increments a specific page view or creates it and increments it if it doesn't exist. returns the page view
    """
    permission_classes = ()
    lookup_fields = ["origin", "pathname"]
    queryset = PageView.objects.all()
    serializer_class = PageViewSerializer

    def get_or_make_page_view(self, origin, pathname):
        try:
            site_status = SiteStatus.objects.get(origin=origin)
        except SiteStatus.DoesNotExist:
            if "scuzzyfox.com" in str(origin):
                site_status = SiteStatus(origin=origin)
                site_status.save()
        try:
            page_view = PageView.objects.get(
                site_status=site_status, pathname=pathname)
        except PageView.DoesNotExist:
            page_view = PageView(site_status=site_status, pathname=pathname)
            page_view.save()

        return page_view

    def update_website_views(self, origin):
        try:
            site_status = SiteStatus.objects.get(origin=origin)
        except SiteStatus.DoesNotExist:
            if "scuzzyfox.com" in str(origin):
                site_status = SiteStatus(origin=origin)
                site_status.save()
        total_web_views = PageView.objects.filter(site_status=site_status).aggregate(
            sum_views=models.Sum('view_count')).get('sum_views', 0)
        site_status.website_views = total_web_views if total_web_views is not None else 0
        site_status.save()

    def get(self, request, origin):
        pathname = request.data.get("pathname")
        if pathname is None:
            return Response({"error": "No pathname supplied"}, status=status.HTTP_400_BAD_REQUEST)

        page_view = self.get_or_make_page_view(
            origin=origin, pathname=pathname)
        serializer = self.serializer_class(page_view)
        return Response(serializer.data)

    def post(self, request, origin):
        pathname = request.data.get("pathname")
        if pathname is None:
            return Response({"error": "No pathname supplied"}, status=status.HTTP_400_BAD_REQUEST)

        page_view = self.get_or_make_page_view(
            origin=origin, pathname=pathname)

        page_view.view_count = page_view.view_count + 1
        page_view.save()
        self.update_website_views(origin=origin)
        serializer = self.serializer_class(page_view)
        return Response(serializer.data)


class UpdateSiteStatus(APIView):
    """Updates the site status for a specific origin. site status has to exist."""
    authentication_classes = [JWTAuthentication]
    serializer_class = SiteStatusSerializer

    def put(self, request, origin):
        """Updates the site status for a specific origin"""
        site_status = get_object_or_404(SiteStatus, origin=origin)
        site_status.commissions_open = request.data.get(
            "commissions_open", site_status.commissions_open)
        site_status.requests_open = request.data.get(
            "requests_open", site_status.requests_open)
        site_status.art_trades_open = request.data.get(
            "art_trades_open", site_status.art_trades_open)
        site_status.store_open = request.data.get(
            "store_open", site_status.store_open)
        site_status.save()
        serializer = self.serializer_class(site_status)
        return Response(serializer.data)
