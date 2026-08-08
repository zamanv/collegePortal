from django.urls import path
from . import views

urlpatterns = [
    # Add this line to map http://127.0.0.1:8000/ directly to login
    path('', views.login_page, name='home'),

    path('studentReg/', views.stud_reg, name='stud_reg'),
    path('facultyReg/', views.faculty_reg, name='facu_reg'),
    path('login/', views.login_page, name='login_p'),
    path('logout/', views.logout_page, name='logout'),
]