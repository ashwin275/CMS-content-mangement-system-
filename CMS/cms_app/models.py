from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password

class CustomUser(AbstractUser):
    address = models.CharField(max_length=200,blank=True)
    bio = models.TextField(blank=True)
    state = models.CharField(max_length=150,blank=True)
    country = models.CharField(max_length=100,blank=True)

    def save(self, *args, **kwargs):
            if not self.id and self.password:
                self.password = make_password(self.password)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Blog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    slug = models.SlugField(default='', max_length=150, unique=True)
    title = models.CharField(max_length=150)
    description = models.TextField()
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    tags = models.CharField(max_length=100)  
    updated_date = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Like(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
