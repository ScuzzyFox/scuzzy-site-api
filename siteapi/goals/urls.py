from django.urls import path
from .views import ListGoals, GoalDetail, UDGoals, CreateGoal, FulfillGoal

urlpatterns = [
    path('goals/', ListGoals.as_view(), name='goals'),
    path('goals/<int:pk>/', GoalDetail.as_view(), name='goal-detail'),
    path('mod-goals/<int:pk>/fulfill',
         FulfillGoal.as_view(), name='fulfill-goal'),
    path('mod-goals/<int:pk>/', UDGoals.as_view(), name='ud-goals'),
    path('mod-goals/', CreateGoal.as_view(), name='create-goal'),
]
