from django.shortcuts import render, HttpResponse, redirect
import datetime
from django.utils.translation import get_language, activate, gettext
from cloudinary import uploader, CloudinaryImage
from .models import Groups, Post, Club, User_Request, Comments, Events, User, Club_post, Club_Comment
from .forms import Groupform, Postform, ClubCreateRequestForm, EventCreateRequestForm, ClubForm, EventForm, MyUserCreationForm, UserUpdateForm, ClubPostForm, ClubCommentForm, PostCommentForm, PostReport
from django.db.models import Q, F
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters


# Create your views here.
@sensitive_post_parameters()
def loginPage(request):
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        try:
            user1 = User.objects.get(email=email)
        except:
            messages.error(request, 'Chutya')
            
        user1 = authenticate(request, email=email, password=password)

        if user1 is not None:
            login(request, user1)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exists.')
    
    return render(request, 'base/home.html')

def register(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(request, 'User created successfully!')
            return redirect(to='home')
        else:
            messages.error(request, 'An error occured. Please try again later.')

    context = {'form':form}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    messages.success(request, 'User logged out!')
    return redirect('home')

def home(request):
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user1 = authenticate(request, username=username, password=password)
            if user1 is not None:
                login(request, user1)
                return redirect('home')
            else:
                messages.error(request, 'Username or password does not exists.')
        except:
            messages.error(request, 'User does not exist!')
        # user1 = authenticate(request, username=username, password=password)
        # if user1 is not None:
        #     login(request, user1)
        #     return redirect('home')
        # else:
        #     messages.error(request, 'Username or password does not exists.')

    q = request.GET.get('q') if request.GET.get('q') != None else ''
    if q:
        groups = Groups.objects.filter(Q(name__icontains=q)|Q(description__icontains=q))       
    elif request.user:
        groups = Groups.objects.filter(members=request.user.id).order_by("name")
    else:
        groups = None
        
    context = {'groups': groups}
    return render(request, 'base/home.html', context)

@login_required(login_url='home')
def group(request, pk, num):
    number = num*15
    group = Groups.objects.get(id=pk)
    members = group.members.all()
    tags = group.tags.all()
    no_of_posts = Post.objects.filter(group=pk).count()
    posts = Post.objects.filter(group=pk)[number-15:number]
    if len(posts)+((num-1)*15) < no_of_posts:
        nextpage = True
    else:
        nextpage = False
    try:
        sent = User_Request.objects.get(sender=request.user, group=group)
    except:
        sent = None
    if request.method == 'POST':
        if request.FILES:
            input_image = request.FILES['image']
        else:
            input_image = None
        Post.objects.create(
            creator = request.user,
            group = group,
            body = request.POST.get('body'),
            image = input_image,
            cloudinary_url = request.POST.get('cloud_url'),
            embed = request.POST.get('embed'),
        )
        messages.success(request, 'New post created!')
        return redirect('group', pk=group.id, num=num)
    context = {'group': group, 'posts':posts, 'sent':sent, 'members':members,'tags':tags, 'color':group.theme, 'pageno':num, 'previous':num-1, 'next':num+1,'nextpage':nextpage}
    return render(request, 'base/group_page.html', context)

@login_required(login_url='home')
def groupDetails(request, pk):
    group = Groups.objects.get(id=pk)
    tags = group.tags.all()
    try:
        sent = User_Request.objects.get(sender=request.user, group=group)
    except:
        sent = None
        
    members = group.members.exclude(pk=group.creator.id).order_by('username')
    context = {'group':group, 'members':members, 'sent':sent,'tags':tags, 'color':group.theme}
    return render(request, 'base/group_details.html', context)

@login_required(login_url='home')
def clubs(request, pk):
    group = Groups.objects.get(id=pk)
    members = group.members.all()
    tags = group.tags.all()
    clubs = Club.objects.filter(group=pk)
    context = {'group':group,'clubs':clubs, 'members':members,'tags':tags, 'color':group.theme}
    return render(request, 'base/group_clubs.html', context)

@login_required(login_url='home')
def events(request, pk):
    group = Groups.objects.get(id=pk)
    tags = group.tags.all()
    members = group.members.all()
    events = Events.objects.filter(group=pk, event_date__gte=datetime.date.today())
    
    for event in events:
        if event.event_date + datetime.timedelta(hours=1) < datetime.date.today():
            event.delete()
    context = {'group':group, 'members':members, 'events':events,'tags':tags, 'color':group.theme}
    return render(request, 'base/group_events.html', context)

@login_required(login_url='home')
def createGroup(request):
    form = Groupform()
    if request.method == 'POST':
        form = Groupform(request.POST, request.FILES)
        if form.is_valid():
            group = Groups.objects.create(
                name = form.cleaned_data.get('name'),
                creator = request.user,
                description = form.cleaned_data.get('description'),
                private = form.cleaned_data.get('private'),
                image = form.cleaned_data.get('image'),
                notice = form.cleaned_data.get('notice'),
            )
            group.save()
            group.members.add(request.user)
            messages.success(request, 'Group has been created.')
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/create_group.html', context)

@login_required(login_url='home')
def editGroup(request, pk):
    group = Groups.objects.get(id=pk)
    if group.image:
        img_url = group.image.url
    try:
        if request.user == group.creator:
            form = Groupform(instance=group)
            if request.method == 'POST':
                form = Groupform(request.POST,request.FILES, instance=group)
                if form.is_valid:
                    if request.FILES:
                        public_id = 'images/' + img_url.split('/')[-2] +'/'+ img_url.split('/')[-1]
                        uploader.destroy(public_id)
                    form.save()
                    messages.success(request, 'Group has been edited!')
                    return redirect('group-details', pk=group.id)
        context = {'form':form, 'color':group.theme}
        return render(request, 'base/edit_post.html', context)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')    

@login_required(login_url='home')
def deleteGroup(request, pk):
    group = Groups.objects.get(id=pk)
    try:
        if request.user == group.creator:
            group.delete()
            messages.success(request, 'The group has been deleted.')
            return redirect('home')
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')

@login_required(login_url='home')
def request_to_join(request, pk):
    group = Groups.objects.get(id=pk)
    if request.method == 'POST':
        request1 = User_Request.objects.create(
            sender = request.user,
            group = group,
            message = request.POST.get('message'),
            group_join_request = True
        )
        messages.success(request, 'Request sent.')
        return redirect('group', pk=group.id, num=1)
    context = {'group': group}
    return render(request, 'base/request_page.html', context)

def deleteRequest(request,pk):
    request1 = User_Request.objects.get(id=pk)
    group_id = request1.group.id
    request1.delete()
    return redirect('group', pk=group_id, num=1)
    
@login_required(login_url='home')
def pending_requests(request, pk):
    group = Groups.objects.get(id=pk)
    join_request = User_Request.objects.filter(group=group, group_join_request=True)
    club_request = User_Request.objects.filter(group=group, club_request=True)
    report_request = User_Request.objects.filter(group=group, post_report=True)
    event_request = User_Request.objects.filter(group=group, event_request=True)
    context = {'join_requests':join_request, 'club_requests':club_request, 'report_requests':report_request, 'event_requests':event_request, 'group':group}
    return render(request, 'base/group_requests.html', context)

@login_required(login_url='home')
def accept_request(request, pk):
    request1 = User_Request.objects.get(id=pk)
    group = Groups.objects.get(id=request1.group.id)
    group.members.add(request1.sender)
    request1.delete()
    return redirect('pending_requests', pk=group.id)

@login_required(login_url='home')
def accept_invite(request, pk):
    request1 = User_Request.objects.get(id=pk)
    group = Groups.objects.get(id=request1.group.id)
    group.members.add(request1.receiver)
    request1.delete()
    return redirect('group-invites')

@login_required(login_url='home')
def reject_invite(request, pk):
    request1 = User_Request.objects.get(id=pk)
    request1.delete()
    return redirect('group-invites')

@login_required(login_url='home')
def reject_request(request, pk):
    request1 = User_Request.objects.get(id=pk)
    group_id = request1.group.id
    request1.delete()
    return redirect('pending_requests', pk=group_id)

@login_required(login_url='home')
def group_join(request, pk):
    group = Groups.objects.get(id=pk)
    group.members.add(request.user)
    return redirect('group', pk=group.id, num=1)

@login_required(login_url='home')
def edit_post(request, pk):
    post = Post.objects.get(id=pk)
    try:
        if request.user == post.creator:
            form = Postform(instance=post)
            if request.method == 'POST':
                form = Postform(request.POST,instance=post)
                if form.is_valid:
                    form.save()
                    post.post_updated = datetime.datetime.now()
                    post.save()
                    messages.success(request, 'Post has been edited.')
                    return redirect('post-details', pk=post.id)
        context = {'form':form}
        return render(request, 'base/edit_post.html', context)        
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')


@login_required(login_url='home')
def delete_post(request, pk):
    post = Post.objects.get(id=pk)
    if request.user == post.creator or request.user == post.group.creator:
        group_id = post.group.id
        post.delete()
        messages.success(request, 'Post has been deleted.')
        return redirect('group', pk=group_id, num=1)
    else:
        messages.error(request, 'Some error occured.')
        return redirect('home')  

@login_required(login_url='home')
def createClubRequest(request, pk):
    group = Groups.objects.get(id=pk)
    if request.user == group.creator:
        form = ClubForm()
    else:
        form = ClubCreateRequestForm()
    if request.method == 'POST':
        if request.user == group.creator:
            form = ClubForm(request.POST, request.FILES)
            if form.is_valid():
                new_club = Club.objects.create(
                    group = group,
                    host = request.user,
                    name = form.cleaned_data.get('name'),
                    description = form.cleaned_data.get('description'),
                    private = form.cleaned_data.get('private'),
                    image = form.cleaned_data.get('image'),
                )
                new_club.save()
                new_club.members.add(request.user)
                messages.success(request, 'A new club has been created.')
                return redirect('club', pk=group.id)
        else:
            form = ClubCreateRequestForm(request.POST, request.FILES)
            if form.is_valid():
                new_club = User_Request.objects.create(
                    name = form.cleaned_data.get('name'),
                    description = form.cleaned_data.get('description'),
                    sender = request.user,
                    group = group,
                    message = form.cleaned_data.get('message'),
                    club_request = True,
                )
                new_club.save()
                messages.success(request, 'Request has been sent.')
                return redirect('group', pk=group.id, num=1)
                
    context = {'group':group, 'form':form}
    return render(request, 'base/create_club.html', context)

@login_required(login_url='home')
def createClub(request, pk):
    request1 = User_Request.objects.get(id=pk)
    group_id = request1.group.id
    club = Club.objects.create(
        group = request1.group,
        host = request1.sender,
        name = request1.name,
        description = request1.description
    )
    club.save()
    club.members.add(request1.sender, request1.group.creator)
    request1.delete()
    messages.success(request, 'A new club has been created.')
    return redirect('group', pk=group_id, num=1)

@login_required(login_url='home')
def createPostReportRequest(request, pk):
    post = Post.objects.get(id=pk)
    form = PostReport()
    if request.method == 'POST':
        form = PostReport(request.POST)
        if form.is_valid():
            request1 = User_Request.objects.create(
                sender = request.user,
                post = post,
                post_report = True,
                group = post.group,
                report_reason = form.cleaned_data.get('report_reason')
            )
            request1.save()
            messages.success(request, 'Report sent.')
            return redirect('group', pk=post.group.id, num=1)
    context = {'form': form}
    return render(request, 'base/report_page.html', context)

@login_required(login_url='home')
def post_details(request, pk):
    post = Post.objects.get(id=pk)
    comments1 = Comments.objects.filter(post=post)
    if request.method == 'POST':
        comment = Comments.objects.create(
            post = post,
            creator = request.user,
            body = request.POST.get('body')
        )
        
        post.no_of_comments = F('no_of_comments') + 1
        post.save()
        return redirect('post-details', pk=post.id)
    context = {'post':post,'comments1': comments1, 'color':post.group.theme}
    return render(request, 'base/post_details_page.html', context)

@login_required(login_url='home')
def createEventRequest(request, pk):
    group = Groups.objects.get(id=pk)
    if request.user == group.creator:
        if request.method == 'POST':
            if request.FILES:
                input_image = request.FILES['image']
            else:
                input_image = None
            Events.objects.create(
                group = group,
                creator = request.user,
                name = request.POST.get('name'),
                description = request.POST.get('description'),
                event_date = request.POST.get('event_date'),
                event_time = request.POST.get('event_time'),
                image = input_image
            )
            messages.success(request, 'Event has been created')
            return redirect('events', pk=group.id)
        
    if request.user != group.creator:
        #form = EventCreateRequestForm()
        if request.method == 'POST':
            if request.FILES:
                input_image = request.FILES['image']
            else:
                input_image = None
            User_Request.objects.create(
                sender = request.user,
                name = request.POST.get('name'),
                description = request.POST.get('description'),
                event_time = request.POST.get('event_time'),
                event_date = request.POST.get('event_date'),
                message = request.POST.get('message'),
                group = group,
                event_request = True,
        )
            messages.success(request, 'Request has been sent.')
            return redirect('events', pk=group.id)
    context = {'group':group}
    return render(request, 'base/create_event.html', context)

@login_required(login_url='home')
def createEvent(request, pk):
    request1 = User_Request.objects.get(id=pk)
    group_id = request1.group.id
    Events.objects.create(
        creator = request1.sender,
        group=request1.group,
        event_date = request1.event_date,
        event_time = request1.event_time,
        name = request1.name,
        description = request1.description
    )
    messages.success(request, 'A new event has been created.')
    request1.delete()
    return redirect('events', pk=group_id)

@login_required(login_url='home')
def eventDetails(request, pk):
    event = Events.objects.get(id=pk)
    participants = event.interested_members.all()
    context={'event':event, 'participants':participants, 'color':event.group.theme}
    return render(request, 'base/event_details.html', context)

@login_required(login_url='home')
def eventInterested(request, pk):
    event = Events.objects.get(id=pk)
    event.interested_members.add(request.user)
    return redirect('event-details', pk=event.id)

@login_required(login_url='home')
def eventDelete(request, pk):
    event = Events.objects.get(id=pk)
    try:
        if request.user == event.creator:
            event.delete()
            messages.success(request, 'Event deleted.')
            return redirect('events', pk=event.group.id)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')  

@login_required(login_url='home')
def eventEdit(request, pk):
    event = Events.objects.get(id=pk)
    if event.image:
        img_url = event.image.url
    try:
        if request.user == event.creator:
            form = EventForm(instance=event)
            if request.method == 'POST':
                form = EventForm(request.POST,request.FILES, instance=event)
                if form.is_valid():
                    if request.FILES:
                        public_id = 'images/' + img_url.split('/')[-2] +'/'+ img_url.split('/')[-1]
                        uploader.destroy(public_id)
                    form.save()
                    messages.success(request, 'Event has been edited.')
                    return redirect('events', pk=event.group.id)
        context = {'form':form, 'color':event.group.theme}
        return render(request, 'base/edit_post.html', context)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')

@login_required(login_url='home')
def leaveGroup(request, pk):
    group = Groups.objects.get(id=pk)
    group.members.remove(request.user)
    messages.success(request, f'You have left the group {group.name}')
    return redirect('group', pk=group.id, num=1)

@login_required(login_url='home')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    mutual_groups = Groups.objects.filter(Q(members=request.user) and Q(members=user.id))
    context = {'user':user, 'mutual_groups':mutual_groups}
    return render(request, 'base/user_profile.html', context)

@login_required(login_url='home')
def updateUser(request, pk):
    user = User.objects.get(id=pk)
    if user.avatar:
        img_url = user.avatar.url
    try:
        if request.user == user:
            form = UserUpdateForm(instance=user)
            if request.method == 'POST':
                form = UserUpdateForm(request.POST,request.FILES, instance=user)
                if form.is_valid:
                    if request.FILES:
                        public_id = 'images/' + img_url.split('/')[-2] +'/'+ img_url.split('/')[-1]
                        uploader.destroy(public_id)
                    form.save()
                    messages.success(request, 'User details has been updated.')
                    return redirect('user-profile', pk=user.id)
        context = {'form':form}
        return render(request, 'base/edit_profile.html', context)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')

@login_required(login_url='home')
def invitePage(request, pk):
    group = Groups.objects.get(id=pk)
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    if q:
        try:
            exact_user = User.objects.get(username=q)
        except:
            exact_user = None
    else:
        exact_user= None
    context = {'exact_user':exact_user, 'group':group}
    return render(request, 'base/invite_page.html', context)

@login_required(login_url='home')
def sendGroupInvite(request, id1, id2):
    group = Groups.objects.get(id=id1)
    receiver = User.objects.get(id=id2)
    request1 = User_Request.objects.create(
        sender = request.user,
        group = group,
        receiver = receiver,
        invite_request = True
    )
    messages.success(request, 'Invite sent.')
    return redirect('invite-page', pk=group.id)

@login_required(login_url='home')
def groupInvites(request):
    requests = User_Request.objects.filter(receiver=request.user, invite_request=True)
    print(requests)
    context = {'requests': requests}
    return render(request, 'base/invite_requests_page.html', context)

@login_required(login_url='home')
def editComment(request, pk):
    comment = Comments.objects.get(id=pk)
    try:
        if request.user == comment.creator:
            form = PostCommentForm(instance=comment)
            if request.method == 'POST':
                form = PostCommentForm(request.POST, instance=comment)
                if form.is_valid:
                    form.save()
                    messages.success(request, 'Comment has been updated.')
                    return redirect('post-details', pk=comment.post.id)
        context = {'form':form}
        return render(request, 'base/edit_post.html', context)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')

@login_required(login_url='home')
def deleteComment(request, pk):
    comment = Comments.objects.get(id=pk)
    post = Post.objects.get(id=comment.post.id)
    try:
        if request.user == comment.creator:
            post_id = comment.post.id
            post.no_of_comments = F('no_of_comments') - 1
            post.save()
            comment.delete()
            messages.success(request, 'The comment has been deleted.')
            return redirect('post-details', pk=post_id)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')
    
def ResponsivePage(request, pk):
    user = User.objects.get(id=pk)
    mutual_groups = Groups.objects.filter(Q(members=request.user) and Q(members=user.id))
    context = {'user':user, 'mutual_groups':mutual_groups}
    return render(request, 'base/group_page_2.html', context)

def Settings(request):
    return render(request, 'base/setting.html')

def SettingUpdate(request):
    if request.METHOD == 'POST':
        lang = request.POST.get('option')
        translate()

def translate(language):
    cur_language = get_language()
    try:
        activate(language)
    finally:
        activate(cur_language)

@login_required(login_url='home')
def ClubPage(request, pk, num):
    number = num*15
    club = Club.objects.get(id=pk)
    members = club.members.all()
    already_sent = User_Request.objects.filter(sender=request.user, club=club, club_join_request=True)
    color = 'dark'
    if already_sent:
        sent = True
    else:
        sent = False
    if request.user not in members and request.user != club.host:
        context = {'club': club, 'members': members,'color':color,'sent':sent}
        return render(request, 'base/club_page.html', context)
    else:
        no_of_posts = Club_post.objects.filter(club=pk).count()
        club_posts = Club_post.objects.filter(club=pk)[number-15:number]
        if len(club_posts)+((num-1)*15) < no_of_posts:
            nextpage = True
        else:
            nextpage = False
        if request.method == 'POST':
            if request.FILES:
                input_image = request.FILES['image']
            else:
                input_image = None
            Club_post.objects.create(
            club = club,
            creator = request.user,
            body = request.POST.get('body'),
            image = input_image,
            cloudinary_url = request.POST.get('cloud_url'),
            embed = request.POST.get('embed'),
            )
            messages.success(request, 'Post created!')
            return redirect('club-page', pk=club.id, num=1)
        context = {'club': club, 'members': members, 'posts':club_posts, 'color':color,'sent':sent, 'pageno':num, 'previous':num-1, 'nextpage':nextpage}
        return render(request, 'base/club_page.html', context)
    
    
    # context = {'club': club, 'members': members, 'posts':club_posts, 'color':color,'sent':sent, 'pageno':num, 'previous':num-1, 'nextpage':nextpage}
    # return render(request, 'base/club_page.html', context)

@login_required(login_url='home')
def ClubJoin(request, pk):
    request1 = User_Request.objects.get(id=pk)
    club = Club.objects.get(id=request1.club.id)
    club.members.add(request1.sender)
    request1.delete()
    return redirect('club-requests', pk=club.id)

@login_required(login_url='home')
def ClubGallery(request, pk):
    club = Club.objects.get(id=pk)
    members = club.members.all()
    color = 'dark'
    try:
        if request.user in members:
            # post_images = Club_post.objects.filter(club=pk, image__isnull=False)
            post_images = Club_post.objects.filter(Q(club=pk)&Q(image__isnull=False))
            context = {'images':post_images, 'club':club, 'members': members, 'color':color}
            return render(request, 'base/club_gallery.html', context)
    except:
        messages.error(request, 'Page not found.')
        return render('home')
    
    

@login_required(login_url='home')
def delete_club_post(request, pk):
    post = Club_post.objects.get(id=pk)
    try:
        if request.user == post.creator:
            post.delete()
            messages.success(request, 'The post has been deleted.')
            return redirect('club-page', pk=post.club.id, num=1)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')

@login_required(login_url='home')
def editClubPost(request, pk):
    post = Club_post.objects.get(id=pk)
    color = 'dark'
    try:
        if request.user == post.creator:
            form = ClubPostForm(instance=post)
            if request.method == 'POST':
                form = ClubPostForm(request.POST, instance=post)
                if form.is_valid():
                    form.save()
                    post.post_updated = datetime.datetime.now()
                    post.save()
                    messages.success(request, 'Post has been updated.')
                    return redirect('club-post-details', pk=post.id)
        context = {'form':form, 'color':color}
        return render(request, 'base/edit_club_post.html', context)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')

@login_required(login_url='home')
def editClub(request, pk):
    club = Club.objects.get(id=pk)
    if club.image:
        img_url = club.image.url
    try:
        if request.user == club.host:

            form = ClubForm(instance=club)
            if request.method == 'POST':
                form = ClubForm(request.POST,request.FILES, instance=club)
                if form.is_valid:
                    if request.FILES:
                        public_id = 'images/' + img_url.split('/')[-2] +'/'+ img_url.split('/')[-1]
                        uploader.destroy(public_id)
                    form.save()
                    messages.success(request, 'Club details has been updated.')
                    return redirect('club-page', pk=club.id, num=1)
        
        context = {'form':form}
        return render(request, 'base/edit_post.html', context)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')

@login_required(login_url='home')
def deleteClub(request, pk):
    club = Club.objects.get(id=pk)
    try:
        if request.user == club.host:
            group_id = club.group.id
            club.delete()
            messages.success(request, 'The club has been deleted.')
            return redirect('club', pk=group_id)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')

@login_required(login_url='home')
def clubPostDetails(request, pk):
    club_post = Club_post.objects.get(id=pk)
    comments1 = Club_Comment.objects.filter(post=club_post)
    if request.method == 'POST':
        Club_Comment.objects.create(
            post = club_post,
            creator = request.user,
            body = request.POST.get('body')
        )

        club_post.no_of_comments = F('no_of_comments') + 1
        club_post.save()
        messages.success(request, 'New comment added to the post thread.')
        return redirect('club-post-details', pk=club_post.id)
    context = {'post':club_post, 'comments1': comments1, 'color':'dark'}
    return render(request, 'base/club_post_details.html', context)

@login_required(login_url='home')
def deleteClubComment(request, pk):
    comment = Club_Comment.objects.get(id=pk)
    post = Club_post.objects.get(id=comment.post.id)
    try:
        if request.user == comment.creator:
            post_id = comment.post.id
            comment.delete()
            post.no_of_comments = F('no_of_comments') - 1
            post.save()
            messages.success(request, 'The comment has been deleted.')
            return redirect('club-post-details', pk=post_id)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')
    
def editClubPostBody(request, pk):
    pass

@login_required(login_url='home')
def clubJoinRequest(request, pk):
    club = Club.objects.get(id=pk)
    User_Request.objects.create(
        sender = request.user,
        club = club,
        club_join_request = True
    )
    messages.success(request, 'The request has been sent.')
    return redirect('club-page', pk=club.id, num=1)

@login_required(login_url='home')
def clubRequestsPage(request, pk):
    request1 = User_Request.objects.filter(club=pk, club_join_request = True)
    request2 = User_Request.objects.filter(club=pk, post_report = True)
    context = {'requests':request1,'club_id':pk, 'requests2': request2}
    return render(request, 'base/club_requests.html', context)

@login_required(login_url='home')
def leaveClub(request, pk):
    club = Club.objects.get(id=pk)
    club.members.remove(request.user)
    messages.success(request, f'You left {club.name}')
    return redirect('club', club.group.id)

@login_required(login_url='home')
@sensitive_post_parameters('password1', 'password2', 'password3')
def changePasssword(request):
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        password3 = request.POST.get('password3')
        try:
            user1 = authenticate(request, email = request.user, password=password1)
            if user1 is not None:
                if password2 == password3:
                    user1.set_password(password2)
                    user1.save()
                    messages.success(request, 'Pasword has been updated.')
                    return redirect('home')
        except:
            messages.error(request, 'Some error occured.')
            return redirect('home')
    return render(request, 'base/change_password.html')

@login_required(login_url='home')
def editClubComment(request, pk):
    comment = Club_Comment.objects.get(id=pk)
    try:
        if request.user == comment.creator:
            form = ClubCommentForm(instance = comment)
            if request.method == 'POST':
                form = ClubCommentForm(request.POST, instance=comment)
                if form.is_valid:
                    form.save()
                    messages.success(request, 'The comment has been updated.')
                    return redirect('club-post-details', pk = comment.post.id)
        context = {'form':form}
        return render(request, 'base/edit_post.html', context)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')
    
def aboutMe(request):
    return render(request, 'base/about.html')

@login_required(login_url='home')
def removeGroupMember(request, group_id, pk):
    group = Groups.objects.get(id=group_id)
    try:
        if request.user == group.creator:
            user = User.objects.get(id=pk)
            group.members.remove(user)
            messages.success(request, f'You removed {user.name}.')
            return redirect('group-details', pk=group.id)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')
    
@login_required(login_url='home')
def removeClubMember(request, club_id, pk):
    club = Club.objects.get(id=club_id)
    try:
        if request.user == club.host:
            user = User.objects.get(id=pk)
            club.members.remove(user)
            messages.success(request, f'You removed {user.name}.')
            return redirect('club-page', pk=club.id)
    except:
        messages.error(request, 'Some error occured.')
        return redirect('home')
    
@login_required(login_url='home')
def createClubPostReportRequest(request, pk):
    post = Club_post.objects.get(id=pk)
    form = PostReport()
    if request.method == 'POST':
        form = PostReport(request.POST)
        if form.is_valid():
            request1 = User_Request.objects.create(
                sender = request.user,
                club_post = post,
                post_report = True,
                club = post.club,
                report_reason = form.cleaned_data.get('report_reason')
            )
            request1.save()
            messages.success(request, 'A report has been sent.')
            return redirect('club-page', pk=post.club.id)
    context = {'form': form}
    return render(request, 'base/report_page.html', context)

@login_required(login_url='home')
def reject_club_request(request, pk):
    request1 = User_Request.objects.get(id=pk)
    club_id = request1.club.id
    request1.delete()
    return redirect('club-requests', pk=club_id)

@login_required(login_url='home')
def search_posts(request, pk):
    group = Groups.objects.get(id=pk)
    q = request.GET.get('q')
    posts = []
    if q:
        posts = Post.objects.filter(group=group, body__icontains=q).order_by('-post_updated')
        if not posts:
            messages.info(request, 'No posts found.')
    context = {'posts': posts, 'group': group, 'color': group.theme, 'query': q or ''}
    return render(request, 'base/search_posts.html', context)
























    

