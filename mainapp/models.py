from django.db import models

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.id}. {self.name}"

class Game(models.Model):
    name = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre,on_delete=models.CASCADE)
    img = models.ImageField(upload_to ='game_img/')

