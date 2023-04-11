from django.urls import path
from .views import (
    ListSiteStatus,
    SiteStatusDetail,
    PageViewDetail,
    UpdateSiteStatus,
)

urlpatterns = [
    path('site-status/', ListSiteStatus.as_view(), name='list_site_status'),
    path('site-status/<str:origin>/',
         SiteStatusDetail.as_view(), name='site_status_detail'),
    path('page-views/<str:origin>/',
         PageViewDetail.as_view(), name='page_view_detail'),
    path('update-site-status/<str:origin>/',
         UpdateSiteStatus.as_view(), name='update_site_status'),

]
