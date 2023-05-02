from django.urls import path, re_path
from .views import CommissionView, CommissionDetailView, commissionDetailSlugView, CommissionOrderView, CommissionOrderDetailView, CommissionCategoryView, CommissionCategoryDetailView, CommissionOptionDetailView, CommissionOptionView, CommissionStatusView, CommissionVisualView, CharacterReferenceView, CommissionStatusDetailView, CommissionVisualDetailView, CharacterReferenceDetailView, CommissionAddRemoveCategory, OrderAddRemoveStatus, CommissionAddRemoveOption

urlpatterns = [
    path('commissions/', CommissionView.as_view(), name='commissions'),
    re_path(r'^commissions/(?P<pk>\d+)/$',
            CommissionDetailView.as_view(), name='commissions-detail'),
    path('commissions/slug/<slug:slug>/',
         commissionDetailSlugView, name='commissions-detail-slug'),
    path('commissions/option/<int:commission_id>/<int:option_id>/',
         CommissionAddRemoveOption.as_view(), name='commissions-add-remove-option'),
    path('commissions/category/<int:commission_id>/<int:category_id>/',
         CommissionAddRemoveCategory.as_view(), name='commissions-add-remove-category'),
    path('commissions/categories/', CommissionCategoryView.as_view(),
         name='commissions-categories'),
    path('commissions/categories/<int:pk>/',
         CommissionCategoryDetailView.as_view(), name='commissions-categories-detail'),
    path('commissions/options/', CommissionOptionView.as_view(),
         name='commissions-options'),
    path('commissions/options/<int:pk>/',
         CommissionOptionDetailView.as_view(), name='commissions-options-detail'),
    path('commissions/visuals/', CommissionVisualView.as_view(),
         name='commissions-visuals'),
    path('commissions/visuals/<int:pk>/',
         CommissionVisualDetailView.as_view(), name='commissions-visuals-detail'),
    path('commissions/orders/', CommissionOrderView.as_view(),
         name='commissions-orders'),
    path('commissions/orders/<int:pk>/',
         CommissionOrderDetailView.as_view(), name='commissions-orders-detail'),
    path('commissions/statuses/', CommissionStatusView.as_view(),
         name='commissions-statuses'),
    path('commissions/statuses/<int:pk>/',
         CommissionStatusDetailView.as_view(), name='commissions-statuses-detail'),
    path('commissions/order/status/<int:order_id>/<int:status_id>/',
         OrderAddRemoveStatus.as_view(), name='commissions-order-add-remove-status'),
    path('commissions/characters/', CharacterReferenceView.as_view(),
         name='commissions-characters'),
    path('commissions/characters/<int:pk>/',
         CharacterReferenceDetailView.as_view(), name='commissions-characters-detail'),

]