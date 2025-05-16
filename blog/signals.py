from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
import logging
from .models import User, Post, Comment, Category

logger = logging.getLogger(__name__)

# Логирование действий пользователя
@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    logger.info(f"Пользователь {user.username} вошел в систему")

@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    if user:
        logger.info(f"Пользователь {user.username} вышел из системы")

# Логирование операций с пользователями
@receiver(post_save, sender=User)
def user_post_save_handler(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Создан новый пользователь: {instance.username}")
    else:
        logger.info(f"Обновлен пользователь: {instance.username}")

@receiver(post_delete, sender=User)
def user_post_delete_handler(sender, instance, **kwargs):
    logger.info(f"Удален пользователь: {instance.username}")

# Логирование операций с категориями
@receiver(post_save, sender=Category)
def category_post_save_handler(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Создана новая категория: {instance.name}")
    else:
        logger.info(f"Обновлена категория: {instance.name}")

@receiver(post_delete, sender=Category)
def category_post_delete_handler(sender, instance, **kwargs):
    logger.info(f"Удалена категория: {instance.name}")

# Логирование операций со статьями
@receiver(post_save, sender=Post)
def post_post_save_handler(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Создана новая статья: '{instance.title}' автором {instance.author.username}")
    else:
        logger.info(f"Обновлена статья: '{instance.title}' автором {instance.author.username}")

@receiver(post_delete, sender=Post)
def post_post_delete_handler(sender, instance, **kwargs):
    logger.info(f"Удалена статья: '{instance.title}'")

# Логирование операций с комментариями
@receiver(post_save, sender=Comment)
def comment_post_save_handler(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Создан новый комментарий к статье '{instance.post.title}' от пользователя {instance.author.username}")
    else:
        logger.info(f"Обновлен комментарий к статье '{instance.post.title}' от пользователя {instance.author.username}")

@receiver(post_delete, sender=Comment)
def comment_post_delete_handler(sender, instance, **kwargs):
    logger.info(f"Удален комментарий к статье '{instance.post.title}' от пользователя {instance.author.username}") 