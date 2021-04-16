from django.urls import path
from . import views

app_name = 'processing'

urlpatterns = [
    path('', views.index, name="index view"),
    path('add_task/', views.add_task, name="add_task"),
    path('get_current/', views.get_current_task, name="get_current_task"),
    path('get_finished/', views.get_finished_tasks, name="get_finished_tasks"),
    path('get_queued/', views.get_queued_tasks, name="get_queued_tasks"),
    path('on_off/', views.switch_processing, name="on_off_switch"),
    path('poll_status/', views.check_processing, name="poll_status"),
]
