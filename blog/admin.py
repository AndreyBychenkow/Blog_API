from django.contrib import admin
from django import forms
from .models import User, Category, Post, Comment

class CategoryForm(forms.ModelForm):
    slug = forms.SlugField(label='URL-имя')
    
    class Meta:
        model = Category
        fields = '__all__'

class PostForm(forms.ModelForm):
    title = forms.CharField(label='Заголовок статьи')
    content = forms.CharField(label='Текст статьи', widget=forms.Textarea)
    
    class Meta:
        model = Post
        fields = '__all__'

class CommentForm(forms.ModelForm):
    content = forms.CharField(label='Текст комментария', widget=forms.Textarea)
    
    class Meta:
        model = Comment
        fields = '__all__'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': (
                'name', 
                'slug',
            ),
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        self.fields = {
            'name': 'Название',
            'slug': 'URL-имя'
        }
        return fieldsets

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostForm
    list_display = ('title', 'author', 'category', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'category')
    search_fields = ('title', 'content')
    raw_id_fields = ('author',)
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': (
                'title', 
                'content',
                'author',
                'category',
            ),
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentForm
    list_display = ('post', 'author', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('content', 'author__username', 'post__title')
    raw_id_fields = ('author', 'post')
    fieldsets = (
        (None, {
            'fields': (
                'post', 
                'author',
                'content',
            ),
        }),
    )
