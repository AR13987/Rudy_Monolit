from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import datetime
from django.contrib.auth.models import User


# Модель профиля пользователя:
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Мужской'), ('female', 'Женский')], blank=True)
    avatar = models.ImageField(upload_to='user_avatars', blank=True)
    email = models.EmailField(max_length=254, blank=True, null=True)

    def __str__(self):
        return self.user.username



# Модель вопроса:
class Question(models.Model):
    question_text = models.CharField(_("Текст вопроса"), max_length=200)
    pub_date = models.DateTimeField(_("Дата публикации"), auto_now_add=True)
    image = models.ImageField(upload_to='question_images', blank=True, null=True)
    expiration_date = models.DateTimeField(_("Дата окончания"), default=datetime.datetime.now() + datetime.timedelta(days=7))
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    short_description = models.CharField(max_length=200, blank=True)
    full_description = models.TextField(blank=True)
    choices = models.TextField(blank=True)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = datetime.datetime.now()
        # Возвращает True, если вопрос опубликован в диапазоне от 24 часов назад до текущего времени:
        return now - datetime.timedelta(days=1) <= self.pub_data <= now

    was_published_recently.admin_order_field = 'pub_data'
    was_published_recently.boolean = True
    was_published_recently.short_description = _("Опубликован недавно?")

    def get_absolute_url(self):
        # Возвращает абсолютный URL для вопроса:
        return reverse('polls:detail', args=[str(self.pk)])



# Модель варианта ответа:
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(_("Текст варианта"), max_length=200)
    votes = models.IntegerField(_("Количество голосов"), default=0)

    def __str__(self):
        return self.choice_text



# Модель голосования:
class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'question', 'choice')