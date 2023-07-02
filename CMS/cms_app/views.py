from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,UserInfoSerializer,BlogSerializer,BlogviewSerializer
from rest_framework.exceptions import AuthenticationFailed,NotFound,PermissionDenied
from rest_framework.decorators import authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .tokens import get_tokens
from django.db.models import Q
from django.db.models import Count
from .models import CustomUser,Blog,Like
from datetime import datetime
# Create your views here.




class LoginView(APIView):
    def post(self,request):
        email = request.data['email']
        password = request.data['password']
       
        try:
            user = CustomUser.objects.get(email=email)
            
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed("User not found")
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')
        
        serializer = UserInfoSerializer(user)
        token = get_tokens(user)
        
        return Response({
            'payload':serializer.data,
            'token':token,
            'message':'Login Successfull',
        },status=status.HTTP_200_OK)




class UserView(APIView):
    def post(self,request):
       

        if not request.data:
            return Response({'error': 'No data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_profile = serializer.save()
        user_profile.is_active = True
        user_profile.save()

        return Response({
            'payload': serializer.data["username"],
        
            'message': f'Account successfully created with {serializer.data["email"]}.'
        },status=status.HTTP_201_CREATED)
    
    def get(self,request,pk):

        try:
            user = CustomUser.objects.get(id = pk)
            serializer = UserInfoSerializer(user)
            return Response({'payload':serializer.data,'message':'success'})
        except CustomUser.DoesNotExist:
            return Response("User profile does not exist.", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
  

    @authentication_classes([JWTAuthentication])
    def patch(self, request):
        try:
            user_object = CustomUser.objects.get(id=request.user.id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not request.data:
            return Response({'error': 'Invalid request: No data provided.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserInfoSerializer(user_object, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({'payload': serializer.data,'message':'Succesfully updated'},status=status.HTTP_200_OK)




    @authentication_classes([JWTAuthentication])
    def delete(self,request):
        try:
            user_object = CustomUser.objects.get(id=request.user.id)
        except CustomUser.DoesNotExist:
            raise Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        

        user_object.delete()
        return Response({'message':'Successfully deletd'},status=status.HTTP_200_OK)





class BlogView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
       print('called')
       if not request.data:
            return Response({'error': 'Invalid request: No data provided.'}, status=status.HTTP_400_BAD_REQUEST)
       
       serializer = BlogSerializer(data=request.data,context = {'request':request})
       serializer.is_valid(raise_exception=True)
       serializer.save()

       return Response({'message':'Blog Post Created Successfully','payload':serializer.data},status=status.HTTP_201_CREATED)
    


    def get(self, request, pk=None):
        if pk is not None:
          
            try:
              
                blog = Blog.objects.prefetch_related('like_set').annotate(like_count=Count('like')).get(id=pk)
               
                if not blog.is_public and blog.user != request.user:
                    
                    raise PermissionDenied("Unauthorized access.")
                serializer = BlogviewSerializer(blog)
                return Response(serializer.data)
            except Blog.DoesNotExist:
                raise NotFound({'error': 'Blog not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            blogs = Blog.objects.prefetch_related('like_set').annotate(like_count = Count('like')).filter(Q(is_public=True) | Q(user=request.user))
            
            serializer = BlogviewSerializer(blogs, many=True)
            return Response(serializer.data)
                

    def patch(self,request,pk):
        try:
           blog = Blog.objects.get(id=pk)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found.'}, status=status.HTTP_404_NOT_FOUND)

        if blog.user != request.user:
            raise PermissionDenied("Unauthorized access.")
        
        if not request.data:
            return Response({'error': 'Invalid request: No data provided.'}, status=status.HTTP_400_BAD_REQUEST)
        

        serializer = BlogSerializer(blog,data=request.data,partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        blog.updated_date = datetime.now()
        blog.save()
        return Response({'message':'Blog updated succesfully','payload':serializer.data},status=status.HTTP_200_OK)



    def delete(self,request,pk):
        try:
           blog = Blog.objects.get(id=pk)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if blog.user != request.user:
            raise PermissionDenied("Unauthorized access.")
        
        blog.delete()
        return Response({'message':'Blog deleted succes'},status=status.HTTP_200_OK)





class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, blogId):
        try:
            blog = Blog.objects.get(id=blogId)
            try:
                like = Like.objects.get(user=request.user, blog=blog)
                return Response({'message': 'Already liked.'}, status=status.HTTP_200_OK)
            except Like.DoesNotExist:
                like = Like.objects.create(user=request.user, blog=blog)
                like.save()
                return Response({'message': 'Success.'}, status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def delete(self,request,blogId):
        try:
            like = Like.objects.get(user = request.user,blog = blogId)
            print(Like)

            like.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Blog.DoesNotExist:
            return Response({'error': 'Blog not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
