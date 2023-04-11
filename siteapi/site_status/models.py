from django.db import models

# Create your models here.


class SiteStatus(models.Model):
    """
    Model representing the status of a site.

    Attributes:
    -----------
    origin : str
        The origin of the site.
    commissions_open : bool
        Whether commissions are open or not.
    requests_open : bool
        Whether requests are open or not.
    art_trades_open : bool
        Whether art trades are open or not.
    store_open : bool
        Whether the store is open or not.
    website_views : int
        The sum of all website views.
    """
    origin = models.CharField(max_length=255, primary_key=True)
    commissions_open = models.BooleanField(default=False)
    requests_open = models.BooleanField(default=False)
    art_trades_open = models.BooleanField(default=False)
    store_open = models.BooleanField(default=False)
    website_views = models.IntegerField(default=0)


class PageView(models.Model):
    """
    Model representing a page view.

    Attributes:
    -----------
    site_status : ForeignKey
        The site status this page view belongs to.
    pathname : str
        The pathname of the page view.
    view_count : int
        The view count for the page view.
    """
    site_status = models.ForeignKey(
        SiteStatus, on_delete=models.CASCADE, related_name='page_views')
    pathname = models.CharField(max_length=255)
    view_count = models.IntegerField(default=0)
