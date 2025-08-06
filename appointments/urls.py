from django.urls import path
from .views import dashboard_view
from . import views

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('add/', views.add_appointment, name='add_appointment'),
    path('edit/<int:pk>/', views.edit_appointment, name='edit_appointment'),
    path('checkers/add/', views.add_checker, name='add_checker'),
    path('appointments/export/', views.export_appointments_csv, name='export_appointments_csv'),
    path('appointments/import/', views.import_appointments_csv, name='import_appointments_csv'),
    path('delete/<int:pk>/', views.delete_appointment, name='delete_appointment'),
    path('appointments/table/', views.appointment_table_partial, name='appointment_table_partial'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/export/', views.export_dashboard_csv, name='export_dashboard_csv'),

]
