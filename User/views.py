from datetime import date, datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Q

from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.views.generic import CreateView

from User.forms import StudentSignUpForm, AdminSignUpForm, UserForm, ReportForm, AttendanceForm
from User.models import User, Attendance, LeaveRequest, Student


class student_register(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = '../templates/signup.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('attendance')


class admin_register(CreateView):
    model = User
    form_class = AdminSignUpForm
    template_name = '../templates/admin_reg.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('admin_home')


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_student:
                login(request, user)
                return redirect('attendance')
            elif user is not None and user.is_admin:
                login(request, user)
                return redirect('admin_home')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, '../templates/login.html',
                  context={'form': AuthenticationForm()})


@staff_member_required
def admin_home(request):
    return render(request, 'admin_home.html')


def logout_view(request):
    logout(request)
    return redirect('/')


def base(request):
    return render(request, 'base.html')


@login_required
def attendance(request, ):
    return render(request, 'attendance.html')


@login_required
def mark_attendance(request):
    today = date.today()
    try:
        attendance = Attendance.objects.get(student=request.user, date=today)
        messages.info(request, f"You have already submitted attendance for {today.strftime('%m/%d/%Y')}.")
        return redirect('message')
    except Attendance.DoesNotExist:
        if request.method == 'POST':
            attendance = request.POST.get('attendance')
            if attendance == 'present':
                Attendance.objects.create(student=request.user, date=today, status='Present')
                messages.success(request, 'You have been marked as present.')
            elif attendance == 'absent':
                Attendance.objects.create(student=request.user, date=today, status='Absent')
                messages.success(request, 'You have been marked as absent.')
            else:
                messages.warning(request, 'Invalid form submission.')
        return render(request, 'mark_attendance.html')


@login_required
def view_attendance(request):
    student = Student.objects.get(id=request.user.student.id)
    attendance = Attendance.objects.filter(student=request.user)
    return render(request, 'view_attendance.html', {'attendance': attendance, 'student': student})


@login_required
def mark_leave(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        LeaveRequest.objects.create(student=request.user, start_date=start_date, end_date=end_date, reason=reason)
        messages.success(request, 'Your leave request has been submitted.')
        return redirect('response')
    return render(request, 'mark_leave.html')


def message(request):
    return render(request, 'message.html')


@login_required
def response(request):
    return render(request, 'leave_response.html')


def view_attendance_admin(request):
    attendance = Attendance.objects.all()

    return render(request, 'view_attendance_admin.html', {'attendance': attendance})


def edit_attendance(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    form = AttendanceForm(request.POST or None, instance=attendance)
    if form.is_valid():
        form.save()
        return redirect('admin_home')
    context = {
        'form': form,
        'attendance': attendance,
    }
    return render(request, 'edit_attendance.html', context)


@staff_member_required
def delete_attendance(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        attendance.delete()
        return redirect('admin_home')

    context = {'attendance': attendance, 'pk': pk}
    return render(request, 'delete_attendance.html', context)


@staff_member_required
def create_report(request):
    students = User.objects.filter(is_staff=False, is_superuser=False)

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            from_date = form.cleaned_data['start_date']
            to_date = form.cleaned_data['end_date']
            student_id = form.cleaned_data['student'].id
            attendance = Attendance.objects.filter(
                Q(date__gte=from_date) & Q(date__lte=to_date) & Q(student__id=student_id)
            )
            student = User.objects.get(id=student_id)
            student_name = student.username
            context = {'attendance': attendance, 'student_name': student_name}
            return render(request, 'report.html', context)
    else:
        form = ReportForm()

    context = {'students': students, 'form': form}
    return render(request, 'create_report.html', context)


def view_report(request):
    # Retrieve the student ID from the query parameters
    student_id = request.GET.get('student_id')

    # Retrieve the attendance records for the specified student
    attendance = Attendance.objects.filter(student_id=student_id)

    # Get the student name for use in the report header

    context = {'attendance': attendance, }

    return render(request, 'report.html', context)


@staff_member_required
def view_leave_requests(request):
    leave_requests = LeaveRequest.objects.all()
    return render(request, 'view_leave_requests.html', {'leave_requests': leave_requests})


def handle_leave_request(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            leave_request.status = 'approved'
            leave_request.save()
            messages.success(request, 'Leave request has been approved.')
        elif action == 'reject':
            leave_request.status = 'rejected'
            leave_request.save()
            messages.success(request, 'Leave request has been rejected.')
        else:
            messages.error(request, 'Invalid action.')

    return redirect('view_leave')


@staff_member_required
def approve_leave_request(request, leave_request_id):
    leave_request = LeaveRequest.objects.get(id=leave_request_id)
    leave_request.approved = True
    leave_request.save()
    leave_request.delete()
    messages.success(request, 'Leave request has been approved.')
    return redirect('view_leave')


@staff_member_required
def reject_leave_request(request, leave_request_id):
    leave_request = LeaveRequest.objects.get(id=leave_request_id)
    leave_request.approved = False
    leave_request.save()
    leave_request.delete()
    messages.success(request, 'Leave request has been rejected.')
    return redirect('view_leave')


@login_required
def update_profile(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('attendance', )

    return render(request, 'update_profile.html', {'form': form})


def grade(request, student_id):
    user_model = get_user_model()
    student = Student.objects.get(id=student_id)
    user = student.user
    today = date.today()
    attendances = Attendance.objects.filter(student=user, status='Present')
    present_days = attendances.count()
    total = Attendance.objects.filter(student=user, ).count()
    grade = get_grade(present_days, total)

    context = {'grade': grade, 'present_days': present_days, 'total': total}
    return render(request, 'grade.html', context)


def get_grade(present_days, total):
    try:
        if present_days / total * 100 >= 90:
            return 'A'
        elif present_days / total * 100 >= 80:
            return 'B'
        elif present_days / total * 100 >= 70:
            return 'C'
        elif present_days / total * 100 >= 60:
            return 'D'
        else:
            return 'F'
    except:
        ZeroDivisionError('Number of present Days are 0')
