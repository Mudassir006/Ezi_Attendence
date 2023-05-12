from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms import ModelForm

from User.models import User, Student, Admin, Attendance


class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True)

    image = forms.ImageField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.image = self.cleaned_data.get('image')
        user.save()
        client = Student.objects.create(user=user)
        client.phone_number = self.cleaned_data.get('phone_number')
        client.save()
        return user


class AdminSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_admin = True
        user.is_staff = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')

        user.save()
        lawyer = Admin.objects.create(user=user)

        lawyer.save()
        return user


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['image']


class ReportForm(forms.Form):
    student = forms.ModelChoiceField(queryset=User.objects.filter(is_staff=False, is_superuser=False), required=True)
    start_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('date', 'status')
