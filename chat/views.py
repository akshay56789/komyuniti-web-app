from django.shortcuts import render, redirect
from base import models as base_models
from django.contrib import messages
from .models import Messages

# Create your views here.

def chatPage(request, pk, room_name):
    group = base_models.Groups.objects.get(id=pk)
    messages1 = Messages.objects.filter(room_name = room_name)
    tags = group.tags.all()
    members = group.members.all()
    context = {'group':group, 'members':members, 'room_name':room_name, 'messages0':messages1, 'tags':tags,'color':group.theme}
    return render(request, "chat/chat_page.html", context)

def ClubChat(request, pk, room_name):
    club = base_models.Club.objects.get(id=pk)
    members = club.members.all()
    color = 'dark'
    try:
        if request.user in members:
            messages1 = Messages.objects.filter(room_name = room_name)
            context = {'club':club, 'members':members, 'room_name':room_name, 'color':color, 'messages0':messages1}
            return render(request, 'chat/club_chat.html', context)
    except:
        return redirect('club', pk=club.id)

def clearGroupChatMessage(request, pk, room_name):
    group = base_models.Groups.objects.get(id=pk)
    messages1 = Messages.objects.filter(room_name=room_name)
    messages1.delete()
    messages.success(request, 'All chats has been cleared.')
    return redirect('chat-page', pk=group.id, room_name = room_name)
    
def clearClubChatMessage(request, pk, room_name):
    club = base_models.Club.objects.get(id=pk)
    messages1 = Messages.objects.filter(room_name=room_name)
    messages1.delete()
    messages.success(request, 'All chats has been cleared.')
    return redirect('club-chat', pk=club.id, room_name = room_name)
