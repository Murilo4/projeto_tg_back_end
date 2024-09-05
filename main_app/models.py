from django.db import models
from django.contrib.auth.hashers import check_password


# Create your models here.
class User(models.Model):
    email = models.CharField(max_length=50, unique=True, null=False)
    password_hash = models.CharField(max_length=200, null=False)
    user_name = models.CharField(max_length=70, null=False)
    nick_name = models.CharField(max_length=70, unique=True, null=False)
    phone_number = models.CharField(max_length=70, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    managed = False

    def check_password(raw_password, self):
        return check_password(raw_password, self.password_hash)

