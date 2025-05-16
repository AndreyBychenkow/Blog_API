from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja.security import HttpBearer
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db import IntegrityError
from .models import User, Category, Post, Comment
import logging
from ninja_jwt.authentication import JWTAuth

# Настройка логирования
logger = logging.getLogger(__name__)

# Схемы данных
class TokenSchema(Schema):
    token: str

class LoginSchema(Schema):
    username: str
    password: str

class RegisterSchema(Schema):
    username: str
    password: str
    email: str

class CategorySchema(Schema):
    id: int
    name: str
    slug: str

class CategoryCreateSchema(Schema):
    name: str
    slug: str

class CommentOutSchema(Schema):
    id: int
    content: str
    created_at: str
    updated_at: str
    author_username: str

    @staticmethod
    def resolve_author_username(comment):
        return comment.author.username

class CommentCreateSchema(Schema):
    content: str

class PostOutSchema(Schema):
    id: int
    title: str
    content: str
    created_at: str
    updated_at: str
    author_username: str
    category_name: Optional[str] = None
    comments: List[CommentOutSchema] = []

    @staticmethod
    def resolve_author_username(post):
        return post.author.username

    @staticmethod
    def resolve_category_name(post):
        return post.category.name if post.category else None
    
    @staticmethod
    def resolve_comments(post):
        return post.comments.all()

class PostCreateSchema(Schema):
    title: str
    content: str
    category_id: Optional[int] = None

class PostUpdateSchema(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None

class CommentUpdateSchema(Schema):
    content: str

# Простая аутентификация через токен (для обратной совместимости)
class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            user = User.objects.get(token=token)
            return user
        except User.DoesNotExist:
            return None

# Комбинированная аутентификация (поддерживает и токены, и JWT)
class CombinedAuth:
    def __init__(self):
        self.bearer_auth = AuthBearer()
        self.jwt_auth = JWTAuth()
    
    def __call__(self, request):
        # Сначала пробуем JWT
        jwt_user = self.jwt_auth(request)
        if jwt_user:
            return jwt_user
        
        # Если JWT не сработал, пробуем Bearer токен
        bearer_user = self.bearer_auth(request)
        if bearer_user:
            return bearer_user
        
        # Если оба не сработали, возвращаем None
        return None

api = NinjaAPI(title="Blog API", version="1.0.0", urls_namespace="blog_api")

# Аутентификация
@api.post("/auth/register", response=TokenSchema)
def register(request, data: RegisterSchema):
    try:
        user = User.objects.create_user(
            username=data.username,
            email=data.email,
            password=data.password
        )
        token = user.generate_token()
        logger.info(f"Пользователь {user.username} зарегистрирован")
        return {"token": token}
    except IntegrityError:
        logger.warning(f"Ошибка при регистрации пользователя {data.username}")
        raise HttpError(400, "Пользователь уже существует")

@api.post("/auth/login", response=TokenSchema)
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user is None:
        logger.warning(f"Неудачная попытка входа для пользователя {data.username}")
        raise HttpError(401, "Неверные учетные данные")
    
    token = user.generate_token()
    logger.info(f"Пользователь {user.username} вошел в систему")
    return {"token": token}

# Категории
@api.get("/categories", response=List[CategorySchema])
@paginate
def list_categories(request):
    return Category.objects.all()

@api.get("/categories/{category_id}", response=CategorySchema)
def get_category(request, category_id: int):
    return get_object_or_404(Category, id=category_id)

auth = CombinedAuth()

@api.post("/categories", response=CategorySchema, auth=auth)
def create_category(request, data: CategoryCreateSchema):
    if not request.auth.is_staff:
        logger.warning(f"Пользователь {request.auth.username} попытался создать категорию без прав")
        raise HttpError(403, "Требуются права администратора")
    
    try:
        category = Category.objects.create(name=data.name, slug=data.slug)
        logger.info(f"Категория {category.name} создана пользователем {request.auth.username}")
        return category
    except IntegrityError:
        logger.warning(f"Ошибка при создании категории {data.name}")
        raise HttpError(400, "Категория с таким slug уже существует")

# Статьи
@api.get("/posts", response=List[PostOutSchema])
@paginate
def list_posts(request):
    return Post.objects.all()

@api.get("/posts/{post_id}", response=PostOutSchema)
def get_post(request, post_id: int):
    return get_object_or_404(Post, id=post_id)

@api.post("/posts", response=PostOutSchema, auth=auth)
def create_post(request, data: PostCreateSchema):
    category = None
    if data.category_id:
        category = get_object_or_404(Category, id=data.category_id)
    
    post = Post.objects.create(
        title=data.title,
        content=data.content,
        author=request.auth,
        category=category
    )
    logger.info(f"Статья '{post.title}' создана пользователем {request.auth.username}")
    return post

@api.put("/posts/{post_id}", response=PostOutSchema, auth=auth)
def update_post(request, post_id: int, data: PostUpdateSchema):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author != request.auth:
        logger.warning(f"Пользователь {request.auth.username} попытался изменить чужую статью (id: {post_id})")
        raise HttpError(403, "Вы можете редактировать только свои статьи")
    
    if data.title:
        post.title = data.title
    if data.content:
        post.content = data.content
    if data.category_id:
        post.category = get_object_or_404(Category, id=data.category_id)
    
    post.save()
    logger.info(f"Статья '{post.title}' обновлена пользователем {request.auth.username}")
    return post

@api.delete("/posts/{post_id}", auth=auth)
def delete_post(request, post_id: int):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author != request.auth and not request.auth.is_staff:
        logger.warning(f"Пользователь {request.auth.username} попытался удалить чужую статью (id: {post_id})")
        raise HttpError(403, "Вы можете удалять только свои статьи")
    
    title = post.title
    post.delete()
    logger.info(f"Статья '{title}' удалена пользователем {request.auth.username}")
    return {"success": True}

# Комментарии
@api.post("/posts/{post_id}/comments", response=CommentOutSchema, auth=auth)
def create_comment(request, post_id: int, data: CommentCreateSchema):
    post = get_object_or_404(Post, id=post_id)
    
    comment = Comment.objects.create(
        post=post,
        author=request.auth,
        content=data.content
    )
    logger.info(f"Комментарий создан к статье '{post.title}' пользователем {request.auth.username}")
    return comment

@api.put("/comments/{comment_id}", response=CommentOutSchema, auth=auth)
def update_comment(request, comment_id: int, data: CommentUpdateSchema):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.author != request.auth:
        logger.warning(f"Пользователь {request.auth.username} попытался изменить чужой комментарий (id: {comment_id})")
        raise HttpError(403, "Вы можете редактировать только свои комментарии")
    
    comment.content = data.content
    comment.save()
    logger.info(f"Комментарий (id: {comment_id}) обновлен пользователем {request.auth.username}")
    return comment

@api.delete("/comments/{comment_id}", auth=auth)
def delete_comment(request, comment_id: int):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.author != request.auth and not request.auth.is_staff:
        logger.warning(f"Пользователь {request.auth.username} попытался удалить чужой комментарий (id: {comment_id})")
        raise HttpError(403, "Вы можете удалять только свои комментарии")
    
    comment.delete()
    logger.info(f"Комментарий (id: {comment_id}) удален пользователем {request.auth.username}")
    return {"success": True} 