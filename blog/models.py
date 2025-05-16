from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import secrets
import string

class User(AbstractUser):
    """Модель пользователя с расширенной функциональностью"""
    token = models.CharField(_('Токен'), max_length=256, blank=True, null=True, unique=True)
    
    def generate_token(self):
        """Генерирует случайный токен из 256 символов"""
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(256))
        self.token = token
        self.save()
        return token
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

class Category(models.Model):
    """Модель для категорий статей"""
    name = models.CharField(_('Название'), max_length=100)
    slug = models.SlugField(_('URL-имя'), unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")

class Post(models.Model):
    """Модель для статей блога"""
    title = models.CharField(_('Заголовок'), max_length=200)
    content = models.TextField(_('Содержание'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name=_('Автор'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts', verbose_name=_('Категория'))
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Статья")
        verbose_name_plural = _("Статьи")
        ordering = ['-created_at']

class Comment(models.Model):
    """Модель для комментариев к статьям"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Статья'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Автор'))
    content = models.TextField(_('Содержание'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    def __str__(self):
        return f"Комментарий от {self.author.username} к {self.post.title}"
    
    class Meta:
        verbose_name = _("Комментарий")
        verbose_name_plural = _("Комментарии")
        ordering = ['-created_at']
