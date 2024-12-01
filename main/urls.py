from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('generate_table/', views.generate_table, name='generate_table'),
    path('get_cell/', views.get_cell, name='get_cell'),
    path('check_cell/', views.check_cell, name='check_cell'),
    path('save_cell/', views.save_cell, name='save_cell'),
    path('add_new_row/', views.add_new_row, name='add_new_row'),
    path('add_new_col/', views.add_new_col, name='add_new_col')

]
