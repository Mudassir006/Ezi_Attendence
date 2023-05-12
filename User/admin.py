from django.contrib import admin

# StuRegister your models here.
from User.models import *

admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Student)
admin.site.register(LeaveRequest)

admin.site.register(Attendance)
