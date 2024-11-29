import markdown
import hashlib
from bs4 import BeautifulSoup

from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from users.models import User, ChannelRecord, Message

from projects.models import Project

from .forms import SkillForm, UserRegistrationForm, ProfileForm

from .models import Profile,Skills


def login_user(request):

    if request.user.is_authenticated:
        return redirect('profile')
    
    next = request.GET.get('next') or None

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
                    
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            if next is not None:
                return redirect(next)
            
            return redirect('profile')
        else:
            messages.error(request, "Invalid username or password")
			
    
    return render(request, "users/login_register.html")


def logout_user(request):
    logout(request)
    messages.info(request, "User was logged out")
    return redirect('login')

def has_permission(profile, project_id):
    
    project = Project.objects.get(id=project_id)
    
    if profile.user == project.creator.user:
        return True
    return False

def get_user_profile_by_id(id):
    return Profile.objects.get(id=id)
        

def register_user(request):
    
    if request.user.is_authenticated:
        return redirect('profile')
    
    page = 'register'
    form = UserRegistrationForm()
    
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)   
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            
            # user.is_superuser = True
            # user.is_staff = True
            user.save()
            messages.success(request, "Account was created for " + user.username)
            return redirect('login')
    
    return render(request, "users/login_register.html", {'page': page, 'form': form})

@login_required(login_url='login')
def delete_user(request):
    
    username = request.user.username
    typed = request.POST.get("username")
    
    user = request.user
    
    if username != typed:
        messages.error(request, "Incorrect username")
        return StreamingHttpResponse("Incorrect username")
    user.delete()
    messages.error(request, "We are sad to loose you " + username)
    return redirect('login')


@login_required(login_url='login')
def profile(request):    
    projects = request.user.profile.project_set.all()
    
    md = markdown.Markdown()
    
    for project in projects:
        project.description = project.description[:200] + "..."
        soup = BeautifulSoup(md.convert(project.description), 'html.parser')
        project.description = soup.get_text()
    
    context = {"profile" : request.user.profile , "projects": projects}
    return render(request, "users/account.html", context)

@login_required(login_url='login')
def update_profile(request):
        
    form = ProfileForm(instance=request.user.profile)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile was updated successfully")
            return redirect("profile")
    
    return render(request, "users/profile_form.html", {"form": form})


def get_developers(request):
    
    profiles = Profile.objects.all()
    
    context = {"developers" : profiles }
    return render(request, "users/our_developers.html", context)

def view_profile(request, pk):
    
    profile = Profile.objects.get(id=pk)
    projects = profile.project_set.all()
    
    context = {"profile" : profile, "projects": projects, "view": True}
    return render(request, "users/account.html", context)

@login_required(login_url='login')
def addSkill(request, pk):
    
    profile = Profile.objects.get(id=pk)
    form = SkillForm()
    
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.profile = request.user
            skill.save()
            messages.success(request, "New Skill was added")
        return redirect("profile")
    
    context =  {"profile": profile, "form": form}
    return render(request, "users/skill_form.html", context)

@login_required(login_url='login')
def updateSkill(request, pk):
    
    skill = Skills.objects.get(id=pk)
    form = SkillForm(instance=skill)
    
    form.fields['name'].widget.attrs['class'] = 'w-full px-2 py-1 bg-gray-200'
    form.fields['name'].widget.attrs['disabled'] = True
    
    if request.method == "POST":
        request_data = request.POST.copy()
        request_data['name'] = skill.name
        
        form = SkillForm(request_data, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, "Skill was updated")
        else:
            messages.error(request, form.errors)
        return redirect("profile")
    
    context =  {"profile": skill.profile, "form": form, "page": "update", "skill": skill}
    return render(request, "users/skill_form.html", context)

@login_required(login_url='login')
def deleteSkill(request, pk):
    
    next = request.GET.get('next') or None
    
    skill = Skills.objects.get(id=pk)
    skill.delete()
    messages.error(request, f"Skill {skill.name} was deleted")
    if next:
        return redirect(next)
    return redirect("profile")

####################################################################################################################

class Channel:

    @staticmethod
    def ChannelIDgenerator(user1, user2):
        correct_order = sorted([str(user1), str(user2)])
        channel_id = hashlib.md5(f"{correct_order[0]}{correct_order[1]}".encode()).hexdigest()
        return channel_id
    
    def DecodeChannelID(channel_id):
        return channel_id[:8]

    @staticmethod
    @login_required(login_url='login')
    def create_channel_record(user1, user2, channel_id):
        channel_record = ChannelRecord.objects.create()
        channel_record.channel_members.add(user1.user, user2.user)
        channel_record.channel_id = channel_id
        channel_record.save()
        return channel_record
    
    @staticmethod
    def get_messages(channel_id):
        messages = Message.objects.filter(channel=channel_id)
        return messages

    @staticmethod
    @login_required(login_url='login')
    def chat(request, profile_id):            
        
        channel_id = Channel.ChannelIDgenerator(user1=request.user.profile.id, user2=profile_id)
        chat_messages = Channel.get_messages(channel_id).filter(channel=channel_id)
        
        channel_record = ChannelRecord.objects.filter(channel_id=channel_id)
        
        if not channel_record:
            channel_record = Channel.create_channel_record(request.user.profile, get_user_profile_by_id(profile_id), channel_id)
        
        opened_chat = get_user_profile_by_id(profile_id)
        
        if not channel_id:
            return render(request, "chat.html", context={ 'no_chat': True })
        
        filtered_chats = [
            {
                "members": [member for member in chat.channel_members.all() if member != request.user],
            } for chat in request.user.channelrecord_set.all()
        ]
        
        context = {
            "chat_room_id": channel_id,
            "chat_messages": chat_messages,
            "opened_chat": opened_chat,
            "all_chats": filtered_chats,
        }
        
        return render(request, "chat.html", context=context)