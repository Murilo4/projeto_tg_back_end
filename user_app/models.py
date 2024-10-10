# from django.db import models
# from django.contrib.auth.hashers import check_password
from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    email = models.CharField(unique=True, max_length=100)
    user_name = models.CharField(max_length=50, null=False)
    nick_name = models.CharField(max_length=25, null=True)
    phone_number = models.CharField(max_length=20)
    user_img = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        db_table = 'users'


class TempRegistration(models.Model):
    email = models.CharField(max_length=100, null=False, unique=True)
    user_name = models.CharField(max_length=50, null=False)
    nick_name = models.CharField(max_length=25, null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)

    def __str__(self):
        return self.user_name

    class Meta:
        db_table = 'temp_registration'
