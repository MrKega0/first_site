from django.db import models
from userapp.models import MyUser
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.id}. {self.name}"

class Game(models.Model):
    name = models.CharField(max_length=255)
    genre = models.ForeignKey(Genre,on_delete=models.CASCADE)
    description = models.TextField(default="Описание")
    img = models.ImageField(upload_to ='game_img/')
    def __str__(self):
        return f"{self.id}. {self.name} | {self.genre.name}"
    
class Comment(models.Model):
    user = models.ForeignKey(MyUser,on_delete=models.CASCADE,related_name="comments")
    game = models.ForeignKey(Game,on_delete=models.CASCADE,related_name="comments")
    content = models.TextField(
        verbose_name="Комментарий",
        blank=False,
        null=False,
        validators=[MinLengthValidator(1)],
        help_text="Введите текст комментария"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Комментарий от {self.user.username} ({self.created_at:%Y-%m-%d %H:%M})"
    
class Favorite(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')  # чтобы нельзя было добавить игру дважды

