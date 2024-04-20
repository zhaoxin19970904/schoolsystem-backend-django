from django.http import HttpResponse
from django.shortcuts import render
from .models import User,Course,UserCourse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
import jwt
import json
from django.conf import settings
from django.contrib.auth.hashers import check_password
from google.oauth2 import id_token
from google.auth.transport import requests
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import datetime
from datetime import datetime
from dateutil import parser
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils import timezone



def home(request):
    return HttpResponse("Welcome to my Django project!")

def test(request):
    return HttpResponse("test success",request)

def article_detail(request, article_id):
    return HttpResponse(f"Article ID: {article_id}")

def search_articles(request):
    query = request.GET.get('query', '') 
    return HttpResponse(f"Search results for: {query}")


def test_mysql_connection(request):
    data_from_mysql = User.objects.all()
    print(data_from_mysql)
    data_str = "123"
    for user in data_from_mysql:
        data_str += f"Username: {user.username}, Email: {user.email}<br>"
    return HttpResponse(data_str)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')

        try:
            user = User.objects.get(username=username, isDeleted=False)
            print('Username:', username)
            print('Password:', password)
            print(user.password==password)
            if password== user.password:
                print('ready')
                token = jwt.encode({'username': user.username, 'role': user.type, 'id': user.id},'ecloud', algorithm='HS256')
                print(token)
                response_data = {'message': 'Login successful', 'token': token.decode('utf-8')}
                print(response_data)
                return JsonResponse(response_data)
            else:
                return JsonResponse({'message': 'Invalid password'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'message': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'message': 'Error occurred during login', 'error': str(e)}, status=500)

    return JsonResponse({'message': 'Invalid request method'}, status=400)

@csrf_exempt
def google(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        googletoken = data.get('credential')
        idinfo = id_token.verify_oauth2_token(googletoken, requests.Request())
        googleemail = idinfo.get('email')
        if not googleemail:
            return JsonResponse({'message': 'Email not found in token'}, status=400)
        user = User.objects.get(email=googleemail, isDeleted=False)
        token = jwt.encode({
            'username': user.username,
            'role': user.type,
            'id': user.id
        }, 'ecloud', algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return JsonResponse({
            'message': 'Login successful',
            'token': token
        })
    except User.DoesNotExist:
        return JsonResponse({'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': 'Error occurred during login', 'error': str(e)}, status=500)
    
@csrf_exempt
def admins(request):
    try:
        pageSize = int(request.GET.get('pageSize', 2))
        page = int(request.GET.get('page', 1))
        user = User.objects.filter(type='admin', isDeleted=False)
        totalItems = user.count()
        totalPages = totalItems // pageSize + (1 if totalItems % pageSize > 0 else 0)
        if page > totalPages:
            return JsonResponse({'error': 'Page not found'}, status=404)
        startIndex = (page - 1) * pageSize
        paginatedUsers = user[startIndex:startIndex + pageSize]
        print(paginatedUsers)
        return JsonResponse({
            'totalPages': totalPages,
            'currentPage': page,
            'pageSize': pageSize,
            'totalItems': totalItems,
            'students': list(paginatedUsers.values())
        })
    except Exception as e:
        return JsonResponse({'error': 'An error occurred on the server'}, status=500)
    
@csrf_exempt
def adminssearch(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        pageSize = int(request.GET.get('pageSize', 2))
        page = int(request.GET.get('page', 1))

        data = json.loads(request.body)
        query = Q(type='admin', isDeleted=False)
        for item in data:
            if item['fun'] == 'equal':
                query &= Q(**{item['name']: item['value']})
            elif item['fun'] == 'include':
                query &= Q(**{f"{item['name']}__icontains": item['value']})
            elif item['fun'] == 'greater':
                query &= Q(**{f"{item['name']}__gt": item['value']})
            elif item['fun'] == 'less':
                query &= Q(**{f"{item['name']}__lt": item['value']})
        print(query)
        totalItems = User.objects.filter(query).count()
        print(totalItems)
        totalPages = totalItems // pageSize + (1 if totalItems % pageSize > 0 else 0)

        if page > totalPages:
            return JsonResponse({'error': 'Page not found'}, status=404)

        startIndex = (page - 1) * pageSize
        paginatedStudents = User.objects.filter(query)[startIndex:startIndex + pageSize]

        students_data = list(paginatedStudents.values())
        
        return JsonResponse({
            'totalPages': totalPages,
            'currentPage': page,
            'pageSize': pageSize,
            'totalItems': totalItems,
            'students': students_data
        })
    except Exception as e:
        return JsonResponse({'error': 'An error occurred on the server'}, status=500)
    


@api_view(['POST'])
def createUser(request):
    if request.method == 'POST':
        data = request.data
        try:
            birth_date = parser.parse(data['birth'])
            obj, created = User.objects.get_or_create(
                username=data.get('username', ''),
                defaults={
                    'password': data['password'],
                    'gender': data['gender'],
                    'type': data['type'],
                    'birth': birth_date,
                    'age': data['age'],
                    'email': data['email'],
                    'isDeleted': data.get('isDeleted', False)
                }
            )
            return JsonResponse({'message': 'Create a New User'})
        except Exception as e:
            return JsonResponse({'message': 'Error creating or updating record', 'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=405)

@require_http_methods(["GET"])
def get_students(request):
    try:
        students = User.objects.filter(type='student', isDeleted=False)
        students_data = list(students.values())  
        return JsonResponse(students_data, safe=False)  
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@require_http_methods(["GET"])
def get_teachers(request):
    try:
        teachers = User.objects.filter(type='teacher', isDeleted=False)
        teachers_data = list(teachers.values())  
        return JsonResponse(teachers_data, safe=False)  
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt 
@require_http_methods(["POST"]) 
def CreateCourse(request):
    try:
        course_data = json.loads(request.body.decode('utf-8'))
        course = Course.objects.create(**course_data)
        response_data = {
            "id": course.id,
            "name": course.name,
            "des": course.des,
            "credit": course.credit,
            "start": course.start,
            "end": course.end,
            "isDeleted": course.isDeleted,
            "isTeach": course.isTeach
        }
        return JsonResponse({"message": "New course created", "course": response_data}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@require_http_methods(["GET"])
def get_courses(request):
    try:
        courses = Course.objects.filter(isDeleted=False)
        courses_data = list(courses.values())
        return JsonResponse(courses_data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@require_http_methods(["GET"])
def get_course(request, id):
    course = get_object_or_404(Course, pk=id, isDeleted=False)
    course_data = {
        "id": course.id,
        "name": course.name,
        "des": course.des,
        "credit": course.credit,
        "start": course.start,
        "end": course.end,
        "isDeleted": course.isDeleted,
        "isTeach": course.isTeach
    }
    return JsonResponse(course_data)

@require_http_methods(["GET"])
def get_user(request, id):
    user = get_object_or_404(User, pk=id, isDeleted=False)
    user_data = {
        "id": user.id,
        "username":user.username,
        'password': user.password,
        'gender': user.gender,
        'type': user.type,
        'birth': user.birth,
        'age': user.age,
        'email': user.email,
        'isDeleted': user.isDeleted,
    }
    return JsonResponse(user_data)

@require_http_methods(["GET"])
def get_personcourse(request, id):
    try:
        # 直接使用 get_object_or_404 简化并加强代码
        student = get_object_or_404(User, pk=id)

        # 直接查询关联的课程，无需先提取课程ID
        user_courses = UserCourse.objects.filter(user=student).select_related('course')

        # 准备课程数据，包括用户角色和支付状态（如果是学生）
        courses_data = [{
            'id': uc.course.id,
            'name': uc.course.name,
            'des': uc.course.des,
            'credit': uc.course.credit,
            'start': uc.course.start,
            'end': uc.course.end,
            'role': uc.role,
            'paid': uc.paid
        } for uc in user_courses]

        return JsonResponse(courses_data, safe=False)
    except Exception as e:
        return JsonResponse({'message': 'Error retrieving course', 'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def delete_student(request, id):
    try:
        print(id)
        student = get_object_or_404(User, pk=id)
        print(student)
        student.isDeleted = True 
        student.save()

        return JsonResponse({'message': 'Student deleted successfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error deleting student', 'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def delete_course(request, id):
    try:
        print(id)
        course = get_object_or_404(Course, pk=id)
        print(course)
        course.isDeleted = True 
        course.save()

        return JsonResponse({'message': 'course deleted successfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error deleting course', 'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def update_student(request, id):
    try:
        update_data = json.loads(request.body.decode('utf-8'))
        student = User.objects.filter(pk=id).first()
        if not student:
            return JsonResponse({'message': 'Student not found'}, status=404)

        for key, value in update_data.items():
            setattr(student, key, value)
        student.save()

        return JsonResponse({'message': 'Student updated successfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error updating student', 'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["POST"])
def update_course(request, id):
    try:
        update_data = json.loads(request.body.decode('utf-8'))
        course = Course.objects.filter(pk=id).first()
        if not course:
            return JsonResponse({'message': 'course not found'}, status=404)

        for key, value in update_data.items():
            setattr(course, key, value)
        course.save()

        return JsonResponse({'message': 'course updated successfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error updating course', 'error': str(e)}, status=500)
    
@csrf_exempt
def add_person_to_course(request, id, cid):
    try:
        user = get_object_or_404(User, pk=id, isDeleted=False)
        course = get_object_or_404(Course, pk=cid, isDeleted=False)

        print(user)
        print(course)
        if UserCourse.objects.filter(user=user, course=course).exists():
            return JsonResponse({'message': 'User is already enrolled in the course'}, status=400)

        # Check if the course has already started
        if course.start < timezone.now().date():
            return JsonResponse({'message': 'Cannot add user to course past its start date'}, status=400)
        print(timezone.now().date())
        # Create UserCourse instance
        user_course = UserCourse(user=user, course=course, role=user.type, paid=False if user.type == 'student' else None)
        print(user_course)
        # Validate and save UserCourse instance
        try:
            user_course.clean()
            user_course.save()
        except ValidationError as e:
            return JsonResponse({'message': str(e)}, status=400)

        return JsonResponse({'message': 'User added to course successfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error adding user to course', 'error': str(e)}, status=500)
    
@csrf_exempt
def person_pay(request, user_id, course_id):
    try:
        user = get_object_or_404(User, pk=user_id)
        course = get_object_or_404(Course, pk=course_id)
        user_course = UserCourse.objects.filter(user=user, course=course).first()
        if not user_course:
            return JsonResponse({'message': 'Student not enrolled in course'}, status=404)
        user_course.paid = True
        user_course.save()

        return JsonResponse({'message': 'Payment status updated successfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error updating payment status', 'error': str(e)}, status=500)
    
@csrf_exempt
def person_remove(request, user_id, course_id):
    try:
        user = get_object_or_404(User, pk=user_id)
        course = get_object_or_404(Course, pk=course_id)
        user_course_instance = UserCourse.objects.filter(user=user, course=course)
        if not user_course_instance.exists():
            return JsonResponse({'message': 'Course not found in user\'s courses'}, status=404)
        if user.type == 'teacher':
            course.isTeach = False
            course.tid = None
            course.save()
        else:
            user_course_instance.delete()
        return JsonResponse({'message': 'Course removed successfully'})
    except Exception as e:
        return JsonResponse({'message': 'Error removing course from user', 'error': str(e)}, status=500)
@require_http_methods(["GET"])
def course_students(request, id):
    try:
        course = get_object_or_404(Course, pk=id, isDeleted=False)
        students = User.objects.filter(
            user_courses__course=course, 
            user_courses__user__type='student', 
            isDeleted=False
        ).distinct()
        students_data = [{
            'id': student.id,
            'username': student.username,
            'gender': student.gender,
            'type': student.type,
            'birth': student.birth,
            'age': student.age,
            'email': student.email
        } for student in students]

        return JsonResponse(students_data, safe=False)
    except Exception as e:
        return JsonResponse({'message': 'Error retrieving course students', 'error': str(e)}, status=500)