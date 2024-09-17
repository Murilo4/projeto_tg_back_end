# from django.db import models
# from django.contrib.auth.hashers import check_password


from django.db import models


class User(models.Model):
    email = models.CharField(unique=True, max_length=100)
    user_name = models.CharField(max_length=50)
    nick_name = models.CharField(max_length=25, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    user_img = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'users'

  

