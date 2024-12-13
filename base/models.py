from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime, string, random
from django.utils import timezone
from cloudinary import CloudinaryImage, uploader


# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True,null=True)
    bio = models.TextField(null=True)
    # dark
    # birth date
    avatar = models.ImageField(upload_to='komyuniti-user-image',null=True, blank=True,default="komyuniti-post-image/avatar_mclyfi.jpg")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Groups(models.Model):
    THEME_CHOICES = (
        ('#f8f9fa','Light'),
        ('#d8dee9', 'Snow'),
        ('#f9d1d1', 'Pale Pink'),
        ('#b8dad9', 'Scandal'),
        ('#ffe5f1', 'Lavender Blush'),
        ('#ffd3d6', 'Misty Rose'),
        ('#ADDFFF','Light Day Blue'),
        ('#F0FFF0','HoneyDew'),
        ('#FFFFCC','Cream'),
        ('#E5E4E2', 'Platinum'),
        ('#fcf1c0', 'Oasis'),
        ('#C3FDB8', 'Light Jade'),
        ('#C8C4DF', 'Viola'),
        ('#ffe0d1', 'Blanched Almond'),
        ('#F1E5AC','Light Gold')
    )

    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='members', blank=True)
    private = models.BooleanField(default=False)
    image = models.FileField(upload_to='komyuniti-group-image', null=True, blank=True, default='komyuniti-post-image/avatar_mclyfi.jpg')
    tags = models.ManyToManyField('Tags', related_name='tags', blank=True)
    chat_room = models.CharField(max_length=10, default='group_chat_gfg')
    notice = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, related_name='creator' ,on_delete=models.SET_NULL, null=True)
    theme = models.CharField(choices=THEME_CHOICES, default='#f8f9fa', max_length=7)



    def __str__(self):
        return self.name

    def delete(self):
        if self.image:
            image_url = self.image.url
            public_id = 'images/' + image_url.split('/')[-2] +'/'+ image_url.split('/')[-1]
            uploader.destroy(public_id)
        super().delete()





class Tags(models.Model):
    name = models.CharField(max_length=20)
    color = models.CharField(max_length=10)

    def __str__(self):
        return self.name




class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    body = models.TextField()
    image = models.FileField(upload_to='komyuniti-post-image', null=True, blank=True)
    #comments = models.ManyToManyField('Comments',related_name='post_comments', blank=True)
    embed = models.URLField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    post_updated = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    no_of_comments = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.group.name}_{self.body}'

    def delete(self):
        if self.image:
            image_url = self.image.url
            public_id = 'images/' + image_url.split('/')[-2] +'/'+ image_url.split('/')[-1]
            uploader.destroy(public_id)
        super().delete()



class Club(models.Model):
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='host',null=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='club_members', blank=True)
    image = models.FileField(upload_to='komyuniti-club-image',null=True, blank=True, default='komyuniti-post-image/avatar_mclyfi.jpg')
    private = models.BooleanField(default=False, null=True, blank=True)
    chat_room = models.CharField(max_length=10, default='club_chat_gfg')

    def __str__(self):
        return f'{self.group.name}_{self.name}'

    class Meta:
        ordering = ['-created']

    def save(self, *args, **kwargs):
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.chat_room = random_string
        super(Club, self).save(*args, **kwargs)

    #cloudinary service cannot be used as it is a third party app
    def delete(self):
        if self.image:
            image_url = self.image.url
            public_id = 'images/' + image_url.split('/')[-2] +'/'+ image_url.split('/')[-1]
            uploader.destroy(public_id)
        super().delete()




class Club_post(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    image = models.FileField(upload_to='komyuniti-club-post-image', null=True, blank=True)
    #comments = models.ManyToManyField('Comments',related_name='club_post_comments', blank=True)
    post_updated = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    embed = models.URLField(null=True, blank=True)
    no_of_comments = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.club.name}_{self.body}'

    def delete(self):
        if self.image:
            image_url = self.image.url
            public_id = 'images/' + image_url.split('/')[-2] +'/'+ image_url.split('/')[-1]
            uploader.destroy(public_id)
        super().delete()






class User_Request(models.Model):
    REPORT_CHOICES = (
        ('Unwanted commercial content', 'Unwanted commercial content'),
        ('Pornography or sexually explicit material', 'Pornography or sexually explicit material'),
        ('Child abuse', 'Child abuse'),
        ('Hate speech or graphic violence', 'Hate speech or graphic violence'),
        ('Promotes terrorism', 'Promotes terrorism'),
        ('Harassment or Bullying', 'Harassment or Bullying'),
        ('Suicide or self injury', 'Suicide or self injury'),
        ('Misinformation', 'Misinformation')
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, null=True, blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField(null=True, blank=True)
    report_reason = models.CharField(choices=REPORT_CHOICES, default='No reason', max_length=50)
    description = models.TextField(blank=True)
    name = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    club_request = models.BooleanField(default=False)
    club_join_request = models.BooleanField(default=False)
    event_request = models.BooleanField(default=False)
    group_join_request = models.BooleanField(default=False)
    invite_request = models.BooleanField(default=False)
    post_report = models.BooleanField(default=False)
    post = models.ForeignKey(Post,on_delete=models.CASCADE, blank=True, null=True )
    club_post = models.ForeignKey(Club_post, on_delete=models.CASCADE, blank=True, null=True)
    event_date = models.DateField(blank=True, default=datetime.date.today)
    event_time = models.TimeField(blank=True, default = datetime.time)


    class Meta:
        ordering = ['-created']

    def __str__(self) -> str:
        return f'{self.sender} - {self.group}'


class Comments(models.Model):
    post = models.ForeignKey(Post,related_name='comment_post',on_delete=models.CASCADE, null=True, blank=True )
    #club_post = models.ForeignKey(Club_post, related_name='club_postr_comment', on_delete=models.CASCADE, null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField(null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering=['created']

    def __str__(self) -> str:
        return self.body

class Club_Comment(models.Model):
    post = models.ForeignKey(Club_post,related_name='club_comment_post',on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField(null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering=['created']

    def __str__(self) -> str:
        return self.body

class Events(models.Model):
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.FileField(upload_to='komyuniti-event-image', null=True, blank=True)
    event_date = models.DateField(blank=True, default=datetime.date.today)
    event_time = models.TimeField(blank=True, default=datetime.time)
    name = models.CharField(max_length=100)
    description = models.TextField()
    interested_members = models.ManyToManyField(User, related_name='interested_members', blank=True)

    class Meta:
        ordering=['event_date']

    def __str__(self) -> str:
        return f'{self.group}_{self.name}'

    def delete(self):
        if self.image:
            image_url = self.image.url
            public_id = 'images/' + image_url.split('/')[-2] +'/'+ image_url.split('/')[-1]
            uploader.destroy(public_id)
        super().delete()








