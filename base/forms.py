from django.forms import ModelForm, Textarea, TextInput, DateInput, TimeInput, FileInput, EmailInput, CheckboxInput
from django.contrib.auth.forms import UserCreationForm
from .models import Groups, Post, User_Request, Club, Events, User, Club_post, Club_Comment, Comments
import datetime
from cloudinary.forms import CloudinaryFileField

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username', 'email', 'password1', 'password2']

class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'username','avatar', 'bio']
        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
            }),
            'username': TextInput(attrs={
                'class': 'form-control',
            }),
            'avatar': FileInput(attrs={
                'class':'form-control',
                'accept':'image/*',
            }),
            'bio': TextInput(attrs={
                'class': 'form-control',
            }),
        }

class Groupform(ModelForm):
    class Meta:
        model = Groups
        fields = '__all__'
        exclude = ['members', 'creator', 'chat_room']
        widgets = {
            'name': TextInput(attrs={
                'class':'form-control',
            }),
            'description': Textarea(attrs={
                'class': 'form-control',
            }),
            'private': CheckboxInput(attrs={
                'class':'form-check-label',
            }),
            'image': FileInput(attrs={
                'class':'form-control',
                'accept':'image/*'
            }),
            'notice': Textarea(attrs={
                'class':'form-control',
            })
        }

class PostReport(ModelForm):
    class Meta:
        model = User_Request
        fields = ['report_reason']

class Postform(ModelForm):
    class Meta:
        model = Post
        fields = ['body']
        widgets = {
            'body': Textarea(attrs={
                'class':"form-control",
                'style':'max-width: 100%;',
            }),
        }

class PostCommentForm(ModelForm):
    class Meta:
        model = Comments
        fields = ['body']
        widgets = {
            'body': Textarea(attrs={
                'class':"form-control",
                'style':'max-width: 100%;',
            }),
        }

class ClubPostForm(ModelForm):
    class Meta:
        model = Club_post
        fields = ['body']
        widgets = {
            'body': Textarea(attrs={
                'class':"form-control",
                'style':'max-width: 100%;',
            }),            
        }

class ClubCommentForm(ModelForm):
    class Meta:
        model = Club_Comment
        fields = ['body']
        widgets = {
            'body': Textarea(attrs={
                'class':"form-control",
                'style':'max-width: 100%;',
            }),            
        }


class ClubForm(ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'image']
        widgets = {
            'name': TextInput(attrs={
                'class':"form-control",
            }),     
            'description': Textarea(attrs={
                'class':'form-control',
            }), 
            'image': FileInput(attrs={
                'class':'form-control',
                'accept':'image/*'
            }),
            'private': CheckboxInput(attrs={
                'class':'form-check-label',
            }),      
        }

class ClubCreateRequestForm(ModelForm):
    class Meta:
        model = User_Request
        fields = ['name', 'description', 'message']

class EventForm(ModelForm):
    class Meta:
        model = Events
        fields = ['name', 'description', 'event_date', 'event_time', 'image']
        widgets = {
            'name':TextInput(attrs={
                'class':'form-control',
            }),
            'description': Textarea(attrs={
                'class':'form-control',
            }),
            'event_date': DateInput(attrs={
                'class':'form-control',
                'min': datetime.date.today(),
            }),
            'event_time': TimeInput(attrs={
                'class':'form-control',
            }),
            'image': FileInput(attrs={
                'class':'form-control',
                'accept':'image/*'
            }),
        }
        
         

class EventCreateRequestForm(ModelForm):
    class Meta:
        model = User_Request
        fields = ['name', 'description','event_time', 'event_date', 'message']
        


