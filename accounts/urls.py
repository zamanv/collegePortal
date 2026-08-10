from django.urls import path
from . import views
from django.shortcuts import redirect


urlpatterns = [
    path('', lambda request: redirect('login_p')),
    path('studentReg/', views.stud_reg, name='stud_reg'),
    path('facultyReg/', views.faculty_reg, name='facu_reg'),
    path('login/', views.login_page, name='login_p'),
    path('logout/', views.logout_page, name='logout'),
]