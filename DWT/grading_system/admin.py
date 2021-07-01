from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Subject)
admin.site.register(Class)
admin.site.register(AssignedPupil)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'email', 'password', 'first_name', 'last_name', 'user_type']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['grade_id', 'test_id', 'user_id', 'mark']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['test_id', 'test_name', 'subject_id', 'user_id', 'date']
