from django.db import models

class Deck(models.Model):
    user_id = models.ForeignKey("user_app.user", on_delete=models.PROTECT, verbose_name=("user"))
    name = models.CharField(max_length=100)
    favorite = models.BooleanField()
    situation = models.CharField(max_length=100)
    description= models.CharField(max_length=255)
    new = models.IntegerField()
    learning = models.IntegerField()
    review = models.IntegerField()
    img_url = models.TextField(max_length=255)
    create_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
    class Meta:
        db_table = 'deck',
