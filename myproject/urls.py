"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from api.views import test, home ,article_detail ,search_articles,test_mysql_connection,login,google,admins,admins,adminssearch,createUser
from api.views import get_students,get_teachers,CreateCourse,get_courses,get_course,get_user,get_personcourse,person_remove
from api.views import delete_student,update_student,delete_course,update_course,add_person_to_course,person_pay,course_students
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('test', test),
    path('article/<int:article_id>/', article_detail, name='article_detail'),
    path('search/', search_articles, name='search_articles'),
    path('users', test_mysql_connection, name='list-users'),
    path('submit', login, name='login'),
    path('google',google,name='google'),
    path('users/admins', admins , name='admin1'),
    path('users/adminssearch', adminssearch , name='adminsearch'),
    path('users/student', createUser,name='createUser'),
    path('users/students', get_students, name='get_students'),
    path('users/teachers', get_teachers, name='get_teachers'),
    path('courses/course', CreateCourse, name='Createcourse'),
    path('courses/courses', get_courses, name='get_courses'),
    path('courses/courses/<int:id>', get_course, name='get_course'),
    path('users/students/<int:id>', get_user, name='get_user'),
    path('courses/personcourse/<int:id>', get_personcourse, name='get_user'),
    path('users/delete/<int:id>', delete_student, name='delete_student'),
    path('users/update/<int:id>', update_student, name='update_student'),
    path('courses/deletec/<int:id>', delete_course, name='delete_course'),
    path('courses/updatec/<int:id>', update_course, name='update_course'),
    path('courses/personadd/<int:id>/<int:cid>', add_person_to_course, name='add_person_to_course'),
    path('courses/personpay/<int:user_id>/<int:course_id>', person_pay, name='person_pay'),
    path('courses/personremove/<int:user_id>/<int:course_id>', person_remove, name='person_remove'),
    path('users/coursestudents/<int:id>', course_students, name='course_students'),
]