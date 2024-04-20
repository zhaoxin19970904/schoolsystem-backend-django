from django.db import models
from django.core.exceptions import ValidationError

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=6, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    type = models.CharField(max_length=7, choices=[('admin', 'Admin'), ('teacher', 'Teacher'), ('student', 'Student')])
    birth = models.DateTimeField()
    age = models.IntegerField()
    email = models.EmailField(max_length=255)
    # Assume `isDeleted` field is represented as a BooleanField in your Django model
    isDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

class Course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    des = models.CharField(max_length=255)
    credit = models.IntegerField()
    start = models.DateField()
    end = models.DateField()
    isDeleted = models.BooleanField(default=False)
    isTeach = models.BooleanField(default=False)
    class Meta:
        db_table = 'courses'

class UserCourse(models.Model):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_users')
    role = models.CharField(max_length=7, choices=ROLE_CHOICES)
    paid = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        db_table = 'usercourse'
        unique_together = (('user', 'course'),)

    def clean(self):
        if self.role == 'teacher' and self.paid is not None:
            raise ValidationError("paid should be null")
        elif self.role == 'student' and self.paid is None:
            raise ValidationError("paid can not be null")

    def save(self, *args, **kwargs):
        self.clean()
        super(UserCourse, self).save(*args, **kwargs)