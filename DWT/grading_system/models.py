from django.db import models

# Create your models here.
from django.db import models


class Class(models.Model):
    class_id = models.AutoField(primary_key=True)  # make it primany key
    class_name = models.CharField(max_length=100, blank=False, null=True)

    def __str__(self):
        return str(self.class_id)


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100, blank=False, null=True)
    username = models.CharField(max_length=100, blank=False, null=True)
    password = models.CharField(max_length=1000, blank=False, null=True)
    first_name = models.CharField(max_length=100, blank=False, null=True)
    last_name = models.CharField(max_length=100, blank=False, null=True)
    user_type = models.CharField(max_length=50, blank=False, null=True)
    ifLogged = models.BooleanField(default=False)
    token = models.CharField(max_length=500, null=True, default="")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return "{} -{}".format(self.username, self.email)


class Subject(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=100, blank=False, null=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    is_archieved = models.BooleanField(blank=False, null=True)

    def __str__(self):
        return self.subject_name


class Test(models.Model):
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=100, blank=False, null=True)
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.test_name


class AssignedPupil(models.Model):
    assign_id = models.IntegerField(primary_key=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.assign_id)


class Grade(models.Model):
    grade_id = models.IntegerField(primary_key=True)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.FloatField(blank=False, null=True)

    def __str__(self):
        return str(self.grade_id)

    # query on test table and by the subject id and returns test list.  api  and csv import
