from django.contrib import admin
from .models import CustomUser,Blog,Like
# Register your models here.


admin.site.register(CustomUser)
admin.site.register(Blog)
admin.site.register(Like)