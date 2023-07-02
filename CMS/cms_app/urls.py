from rest_framework_simplejwt.views import TokenRefreshView 
from django.urls import path
from .import views


urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/',views.UserView.as_view(),name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('user-detail/<int:pk>/',views.UserView.as_view(),name='user-detail'),
    path('user-edit/',views.UserView.as_view(),name='user-edit'),
    path('user-delete/',views.UserView.as_view(),name='user-delete'),

    path('add-blog/',views.BlogView.as_view(),name='add-blog'),
    path('blog-detail/',views.BlogView.as_view(),name='blog-detail'),
    path('blog-detail/<int:pk>/',views.BlogView.as_view(),name='blog-detail'),
    path('blog-edit/<int:pk>/',views.BlogView.as_view(),name='blog-edit'),
    path('blog-delete/<int:pk>/',views.BlogView.as_view(),name='blog-delete'),

    
    path('blog-like/<int:blogId>/',views.LikeView.as_view(),name='blog-like'),
    path('blog-unlike/<int:blogId>/',views.LikeView.as_view(),name="blog-unlike")
]
