import csv
import io
from django.shortcuts import redirect
from rest_framework import generics
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from .models import User
from django.http import HttpResponse
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.views.generic.base import TemplateView
import hashlib
from rest_framework.generics import *
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.core import serializers
import json

user = None


def archive_subject(subject_id):
    tests = Test.objects.filter(subject_id=subject_id)
    if tests:
        subject = Subject.objects.filter(subject_id=subject_id).update(is_archieved=True)
        return True
    return False


class UserCreate(APIView):
    # get method handler
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def post(self, request, format=None):
        email = request.data.get('email', None)
        username = request.data.get('username', None)
        str_password = request.data.get('password', None)
        password = hashlib.sha256(str_password.encode())
        password = password.hexdigest()
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        user_type = request.data.get('user_type', None)
        data = {'email': email, 'username': username, 'password': password, 'first_name': first_name,
                'last_name': last_name, 'user_type': user_type}
        serializer = UserRegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    # get method handler
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        user_name = request.data.get('user_name', None)
        str_password = request.data.get('password', None)
        password = hashlib.sha256(str_password.encode())
        password = password.hexdigest()
        data = {'user_name': user_name, 'password': password}
        serializer_class = UserLoginSerializer(data=data)
        if serializer_class.is_valid(raise_exception=True):
            global user
            user = User.objects.get(username=user_name)
            return Response(serializer_class.data, status=HTTP_200_OK)
        return Response(serializer_class.errors, status=HTTP_400_BAD_REQUEST)


class UserLogout(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserLogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = UserLogoutSerializer(data=request.data)
        if serializer_class.is_valid(raise_exception=True):
            return Response(serializer_class.data, status=HTTP_200_OK)
        return Response(serializer_class.errors, status=HTTP_400_BAD_REQUEST)


class UserList(APIView):
    def get(self, request, format=None):
        global user
        if user is None:
            return Response({"Error": "User is not found"})
        if user.user_type != "admin":
            return Response({"Error": "User is not admin"})
        users = User.objects.all()
        serializer = UserSerializerWithType(users, many=True)
        return Response(serializer.data)


class UserRetreive(APIView):
    def get(self, request, pk):
        users = User.objects.get(user_id=pk)
        serializer = UserSerializerWithType(users)
        return Response(serializer.data)


class UserListBySubjectId(APIView):
    def get(self, request, pk):
        subject = Subject.objects.get(subject_id=pk)
        assign_pupils = AssignedPupil.objects.filter(class_id=subject.class_id)
        serializer = AssignedPupilSerializer(assign_pupils, many=True)
        return Response(serializer.data)


class UserUpdate(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDestroy(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def delete(self, request, pk):
        user_instance = User.objects.get(user_id=pk)
        if str(user_instance.user_type) == "teacher":
            subjects = Subject.objects.filter(user_id=user_instance.user_id, is_archieved=False)
            if subjects:
                return Response({"error": "teacher is already assigned to subject"})
        if str(user_instance.user_type) == "pupil":
            test_results = Grade.objects.filter(user_id=user_instance.user_id)
            for test_result in test_results:
                test_result.delete()
        user_instance.delete()
        return Response(status=status.HTTP_200_OK)


class ClassCreate(CreateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer


class ClassList(APIView):
    def get(self, request, format=None):
        global user
        if user is None:
            return Response({"Error": "User is not found"})
        if user.user_type != "admin":
            return Response({"Error": "User is not admin"})
        clas = Class.objects.all()
        serializer = ClassSerializer(clas, many=True)
        return Response(serializer.data)


class ClassUpdate(UpdateAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer


class ClassDestroy(APIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

    def delete(self, request, pk):
        assigned_pupils = AssignedPupil.objects.filter(class_id=pk)
        for assigned_pupil in assigned_pupils:
            assigned_pupil.delete()
        subjects = Subject.objects.filter(class_id=pk)
        for subject in subjects:
            if not archive_subject(subject.subject_id):
                subject = Subject.objects.get(subject_id=subject.subject_id)
                subject.delete()
        clas = Class.objects.get(class_id=pk)
        clas.delete()
        return Response({"Success": "Class deleted successfully"}, status=status.HTTP_200_OK)


class SubjectCreate(CreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectList(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectUpdate(UpdateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectDestroy(APIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def delete(self, request, pk):
        tests = Test.objects.filter(subject_id=pk)
        if tests:
            return Response({"Error": "Subject has dependent test"})
        subject_instance = Subject.objects.get(subject_id=pk)
        subject_instance.delete()
        return Response({"Success": "Subject successfully deleted"})


class ArchiveSubject(APIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def post(self, request, pk):
        if archive_subject(pk):
            return Response({"Success": "Subject successfully archived"})
        else:
            return Response({"Error": "Subject can not be archived"})


class TestCreate(CreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class TestList(APIView):

    def get(self, request, pk):
        testlist = Test.objects.filter(subject_id=pk)
        if testlist:
            serializer = TestSerializer(testlist, many=True)
            return Response(serializer.data)
        return Response({"Error": "Subject id not found"})


class TestUpdate(UpdateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class TestDestroy(APIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

    def delete(self, request, pk):
        grades = Grade.objects.filter(test_id=pk)
        if grades:
            for grade in grades:
                grade.delete()
        test = Test.objects.get(test_id=pk)
        test.delete()
        return Response({"Success": "Test successfully deleted"})


class AssignedPupilCreate(CreateAPIView):
    queryset = AssignedPupil.objects.filter()
    serializer_class = AssignedPupilSerializer

    def post(self, request, format=None):
        class_id = request.data.get('class_id', None)
        user_id = request.data.get('user_id', None)
        data = {'class_id': class_id, 'user_id': user_id, }
        assignpupil = AssignedPupil.objects.filter(user_id=int(user_id)).update(class_id=int(class_id))
        if assignpupil:
            return Response(status=status.HTTP_201_CREATED)
        serializer = AssignedPupilSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignedPupilList(ListAPIView):
    queryset = AssignedPupil.objects.all()
    serializer_class = AssignedPupilSerializer


class AssignedSubjectsAndGradesByUserId(APIView):

    def get(self, request, pk):
        clas = AssignedPupil.objects.get(user_id=pk)
        subjects = Subject.objects.filter(subject_id=clas.subject_id)
        dicts = {}
        count = 0
        for subject in subjects:
            tests = Test.objects.filter(subject_id=subject.subject_id, user_id=pk)
            totalMarks = 0
            for test in tests:
                grade = Grade.objects.get(test_id=test.test_id)
                totalMarks += grade.mark
            avgGrade = totalMarks / len(tests)
            # subjectid, subject name and avg grade
            dictionary = {"subject_id": subject.subject_id, "subject_name": subject.subject_name,
                          "average_grade": avgGrade}
            dicts.update({count: dictionary})
            count = count + 1
        return Response(json.dumps(dicts))


# hours = request.GET.get('hours', '')
class TestsandGradesBySubjectId(APIView):
    def get(self, request, *args, **kwargs):
        subject_id = kwargs.get('subject_id', None)
        user_id = kwargs.get('user_id', None)
        print(subject_id)
        tests = Test.objects.filter(subject_id=subject_id, user_id=user_id)
        dicts = {}
        count = 0
        for test in tests:
            grade = Grade.objects.get(test_id=test.test_id)
            dictionary = {"test_id": test.test_id, "test_date": test.date, "grade_marks": grade.mark}
            # test id, test name,  test date, grade marks """
            dicts.update({count: dictionary})
            count = count + 1
        return Response(json.dumps(dicts))


class AssignedPupilUpdate(APIView):
    def patch(self, request, pk, format=None):
        assignpupil = AssignedPupil.objects.get(user_id=pk)
        serializer = AssignedPupilSerializer(assignpupil,
                                             data=request.data,
                                             partial=True)  # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignedPupilDestroy(DestroyAPIView):
    queryset = AssignedPupil.objects.all()
    serializer_class = AssignedPupilSerializer


class StudentList(ListAPIView):
    queryset = User.objects.filter(user_type="pupil")
    serializer_class = UserSerializerWithType


class TeacherList(ListAPIView):
    queryset = User.objects.filter(user_type="teacher")
    serializer_class = UserSerializerWithType


class GradeCreate(APIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def post(self, request, format=None):
        test_id = request.data.get('test_id', None)
        user_id = request.data.get('user_id', None)
        mark = request.data.get('mark', None)
        grade = Grade.objects.filter(user_id=int(user_id), test_id=int(test_id))
        if grade:
            grade.delete()
        data = {'test_id': test_id, 'user_id': user_id, "mark": mark}
        serializer = GradeSerializer(data=data)
        if serializer.is_valid(self):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GradeList(ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class GradeListByPupilId(APIView):  # need to add the url
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get(self, request, pk):
        grades = Grade.objects.filter(user_id=pk)
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)


class GradeListByTestId(APIView):  # need to add the url
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get(self, request, pk):
        grades = Grade.objects.filter(test_id=pk)
        serializer = GradeSerializer(grades, many=True)

        return Response(serializer.data)


class GradeListByUserIdAndTestId(APIView):  # send two pk and add the url
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id', None)
        test_id = kwargs.get('test_id', None)
        grades = Grade.objects.all(test_id=test_id, user_id=user_id)
        serializer = GradeSerializer(grades, many=True)
        return Response(serializer.data)


class GradeUpdate(UpdateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class GradeDestroy(DestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer


class SubjectListByUserId(APIView):
    def get(self, request, pk):
        subjectlist = Subject.objects.filter(user_id=pk)
        serializer = SubjectSerializer(subjectlist, many=True)
        return Response(serializer.data)


class FileUploadAPIView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['file']
        decoded_file = file.read().decode()
        # upload_products_csv.delay(decoded_file, request.user.pk)
        io_string = io.StringIO(decoded_file)
        reader = csv.reader(io_string)
        for row in reader:
            print(row)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetSubjectNamesAndAllTestOfAUser(APIView):
    def get(self, request, pk):
        clas = AssignedPupil.objects.get(user_id=int(pk))
        print(clas.class_id)
        if not clas:
            return Response({"Error": "User id not found in any class"})
        subjects = Subject.objects.filter(class_id=clas.class_id)
        json_data = []
        for subject in subjects:
            subject_and_test = {"subject_name": subject.subject_name, "tests": []}
            tests = Test.objects.filter(subject_id=subject.subject_id)
            for test in tests:
                grade = Grade.objects.filter(test_id=test.test_id,  user_id=pk)
                for singleGrade in grade:
                    test_dict = {"test_name": test.test_name,
                                 "test_marks": singleGrade.mark}
                    if len(test_dict) > 0:
                        subject_and_test["tests"].append(test_dict)
            if len(subject_and_test["tests"]) > 0:
                json_data.append(subject_and_test)
            #print(tests)
        return Response(json_data)

class HomePageView(TemplateView):
    template_name = "home.html"
