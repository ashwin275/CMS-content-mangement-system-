from rest_framework import serializers,validators
from .models import CustomUser,Blog,Like
from django.db import IntegrityError


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
         model = CustomUser
         
         fields = '__all__'

         extra_kwargs = {
            'password':{'write_only':True},
             'email':{
                'required':True,
                'allow_blank':False,
                'validators':[
                    validators.UniqueValidator(
                        CustomUser.objects.all(),'A user with this email already exists please try with other one'
                    )
                ]
            }
        }
    
    def create(self, validated_data):
         return super().create(validated_data)
    


class UserInfoSerializer(serializers.ModelSerializer):
     class Meta:
          model = CustomUser

          fields = ['username','email','bio','address','state','country']



     def update(self, instance, validated_data):
          return super().update(instance, validated_data)


class BlogSerializer(serializers.ModelSerializer):
    
    class Meta:
          model = Blog

          fields = '__all__'
          read_only_fields = ['user']

    def create(self, validated_data):
         validated_data['user'] = self.context['request'].user
         try:
            return super().create(validated_data)
         except IntegrityError as e:
            if 'slug' in str(e):
                raise serializers.ValidationError('A blog with the same slug already exists.')
            else:
                raise serializers.ValidationError('Provided data is not valid')
            

    def update(self, instance, validated_data):
            instance = super().update(instance,validated_data)
            instance.save()
            return instance
                

    def to_representation(self, instance):
        data = super().to_representation(instance)
       
        data.pop('is_public', None)
        data.pop('user', None)
        data.pop('updated_date',None)
        
        return data
    

class BlogviewSerializer(serializers.ModelSerializer):
    like_count = serializers.IntegerField()

    class Meta:
        model = Blog
        fields = ['id', 'slug', 'title', 'description', 'content', 'created_date', 'image', 'tags', 'updated_date', 'is_public', 'like_count']
        read_only_fields = ['user']