from django.db import models



# Create your models here.
class User(models.Model):
    email = models.CharField(max_length=50, unique=True, null=False)
    password_hash = models.CharField(max_length=50, null=False)
    user_name = models.CharField(max_length=70, null=False)
    nick_name = models.CharField(max_length=70, unique=True, null=False)
    phone_number = models.IntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

