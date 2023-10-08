from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse



#Модель Author содержит объекты всех авторов
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user}"


#Модель Категории постов содержит поле название категорий
class Category(models.Model):
    name_of_category = models.CharField(max_length=100, unique=True)
    subscribers = models.ManyToManyField(User, blank=True, null=True, related_name="categories")

    def __str__(self):
        return f"{self.name_of_category}"


#Модель Post содержит в себе новости, которые создают пользователи
class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField(default='none')

#Метод preview() возвращает начало поста
    def preview(self):
        return f'{self.text[:124]}...'

    def __str__(self):
        return str(self.title + ' | ' + self.preview())

    # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с новостями
    def get_absolute_url(self):
        return f'/news/{self.id}'


#Модель для связи «один ко многим» с моделью Post и «один ко многим» с моделью Category
class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

#Модель Reply хранит отклики пользователей на посты
class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_text = models.TextField(default='Default comment')
    date_posted = models.DateTimeField(auto_now_add=True)
    is_allowed = models.BooleanField(default=False)

    def __str__(self):
        return self.author.username + ', ' + self.post.title

class OneTimeCode(models.Model):
    one_time_code = models.CharField(max_length=10, unique=True, verbose_name='Одноразовый код подтверждения:')

    def __str__(self):
        return self.one_time_code

