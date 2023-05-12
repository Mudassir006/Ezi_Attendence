from django.urls import path
from . import views

urlpatterns = [

    path('register/', views.student_register.as_view(), name='register'),
    path('admregister/', views.admin_register.as_view(), name='admregister'),
    path('',views.login_request,name = 'login'),
    path('adminhome/',views.admin_home,name='admin_home'),
    path('report',views.view_report,name='report'),
    path('',views.logout_view,name='logout'),
    path('attendance/',views.attendance,name='attendance'),
    path('mark_attendance/',views.mark_attendance,name='mark_attendance'),
    path('message/',views.message,name='message'),
    path('view_attendace/',views.view_attendance,name='view_attendance'),
    path('mark_leave/',views.mark_leave,name='mark_leave'),
    path('response/',views.response,name='response'),
    path('attendance_admin/', views.view_attendance_admin, name='view_attendance_admin'),
    path('edit_attendance/<int:pk>/', views.edit_attendance, name='edit_attendance'),
    path('delete_attendance/<int:pk>/', views.delete_attendance, name='delete_attendance'),
    path('generate_report/', views.create_report, name='create_report'),

    path('view_leave_request',views.view_leave_requests,name='view_leave'),
    path('handle_leave/<int:pk>/',views.handle_leave_request,name='handle'),
    path('approve_leave_request/<int:leave_request_id>/', views.approve_leave_request, name='approve_leave_request'),
    path('reject_leave_request/<int:leave_request_id>/', views.reject_leave_request, name='reject_leave_request'),
    path('update_profile',views.update_profile,name='update_profile'),
    path('grade/<int:student_id>/',views.grade,name='grade')




]