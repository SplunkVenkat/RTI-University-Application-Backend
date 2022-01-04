from django.urls import path
from . import views
#<int:pk>
urlpatterns=[
    path('application',views.ApplicationView.as_view()),
    path('application/<int:pk>',views.ApplicationView.as_view()),
    path('applicationsrecords',views.ApplicationRecordsView.as_view()),
    path('applicationsrecordsalert',views.ApplicationRecordsRemainingView.as_view()),
    path('applicationdropdown',views.ApplicationDropdownView.as_view()),
    path('applicationdropdown/<int:pk>',views.ApplicationDropdownView.as_view()),
    path('firstappeal',views.FirstAppealView.as_view()),
    path('commissionappeal',views.CommissionAppealView.as_view()),
]