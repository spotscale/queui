from django.urls import path
from . import views

app_name = 'processing'

urlpatterns = [
    path('', views.index, name="index view"),
    path('start_task/', views.add_task, name="start_task"),
    path('get_finished/', views.get_finished_tasks, name="get_finished_tasks"),
    path('on_off/', views.switch_processing, name="on_off_switch"),
]
