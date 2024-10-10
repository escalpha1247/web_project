from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.contrib import messages
from .models import Room, Topic, Message, FollowersCount
from .forms import RoomForm
# Create your views here.

@login_required(login_url='login')
def createTopic(request, pk):
    if request.method == "POST":
        topic_name = request.POST.get('topic_name').capitalize()
        topic_type = request.POST.get('topic_type')
        user = User.objects.get(id=pk)
        if topic_name is not None:
            topic = Topic.objects.create(name=topic_name, is_public=topic_type, creator=user)
            topic.save()
            return redirect('home')

    return render(request, 'base/topic_create.html', {})

@login_required(login_url='login')
def follow(request, pk):
    if request.method == "POST":
        follower = request.POST.get('following_user')
        user = request.POST.get('followed_user')

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+pk)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+pk)
    else:
        return redirect('home')

def userProfile(request, pk):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    user = User.objects.get(id=pk)
    follower = request.user.username
    topics = Topic.objects.all()
    rooms = user.room_set.filter(
        Q(name__icontains=q),
    )[:6]
    room_messages = user.message_set.filter(
        Q(body__icontains=q),
        Q(room__name__icontains=q),
    )[:6]

    if FollowersCount.objects.filter(follower=follower, user=user.username).first():
        button_text = "Unfollow"
    else:
        button_text = "Follow"
        
    user_followers = len(FollowersCount.objects.filter(user=user.username))
    user_following = len(FollowersCount.objects.filter(follower=user.username))
    user_rooms = len(Room.objects.filter(host=user.id))

    context = {'user':user, 'topics':topics, 'rooms':rooms, 'room_messages':room_messages, 'button_text':button_text, 'user_rooms':user_rooms, 'user_followers':user_followers, 'user_following':user_following}
    return render(request, 'base/user.html', context)

@login_required(login_url='login')
def userAccount(request, pk):
    user = User.objects.get(id=pk)
    rq = "account"
    if request.user != user:
        return redirect('home')
    
    return render(request, 'base/user.html', {'user':user, 'rq':rq})

def loginPage(request):
    page="login"
    alert = ""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # try:
        #     user = User.objects.get(username=username)
        # except:
        #     messages.error(request, "Username does not exist.")
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            alert = "incorrect"
    
    return render(request, 'base/login_reg.html', {'page':page, 'alert':alert})

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An Error occurred during registration. Please try again.')
        
    return render(request, 'base/login_reg.html', {'form':form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(host__username__icontains=q) |
        Q(description__icontains=q) 
    )
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__name__icontains=q))[:6]
    room_count = rooms.count()
    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(user=request.user, room=room, body=request.POST.get('comment'))
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            topic = request.POST.get('topic')
            room.topic = Topic.objects.create(name=topic)
            room.save()
            return redirect('home')
    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You do not have permissions to edit/delete this Room.')
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You do not have permissions to edit/delete this Room.')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You do not have permissions to edit/delete this message!')

    if request.method == "POST":
        message.delete()
        return redirect('/')
    return render(request, 'base/delete.html', {'obj':message})