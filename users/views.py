import markdown
import hashlib
from uuid import uuid4
from bs4 import BeautifulSoup

from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from users.models import User, Message, ChatRecords
from users.filters import ProfileFilter

from projects.models import Project

from .forms import SkillForm, UserRegistrationForm, ProfileForm

from .models import Profile,Skills

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from functools import wraps
from django.core.exceptions import PermissionDenied


class AuthenticationView:
    pass

    @staticmethod
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

    @staticmethod
    def logout_user(request):
        logout(request)
        messages.info(request, "User was logged out")
        return redirect('login')
    
    @staticmethod
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

class UserView:

    @staticmethod
    def get_user_by_id(id):
        return User.objects.get(id=id)
    
    @staticmethod
    def get_user_profile_by_id(id):
        return Profile.objects.get(id=id)

    @staticmethod
    def update_online_status(user_id, socket_id, status):
        user = UserView.get_user_by_id(user_id)

        user.socket_id = socket_id
        user.is_online = status
        user.save()
        return user.is_online
    
    def has_permission(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            profile = request.user.profile
            project_id = kwargs.get('pk')
            project = Project.objects.get(id=project_id)
            
            if profile.user != project.creator.user:
                raise PermissionDenied
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view

    @staticmethod
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

    @staticmethod
    @login_required(login_url='login')
    def update_profile(request):
            
        form = ProfileForm(instance=request.user.profile)
        if request.method == "POST":
            form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
            if form.is_valid():
                update_instance = form.save(commit=False)
                print(request.FILES)
                update_instance.avatar = request.FILES.get("avatar")
                update_instance.save()
                messages.success(request, "Profile was updated successfully")
                return redirect("profile")
        
        context = {
            "form": form,
            "page": "update",
            "profile_preview_image": request.user.profile.avatar_url
        }
        
        return render(request, "users/profile_form.html", context)


    @staticmethod
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


    @staticmethod
    def get_developers(request):
        search_query = {'search': request.GET.get("search")}
        page_number = request.GET.get('page')
        
        searched_profiles = ProfileFilter(search_query, queryset=Profile.objects.all())

        profiles = searched_profiles.qs
        
        paginator = Paginator(profiles, 25)
        profiles = paginator.get_page(page_number)

        context = {
            'search_query': request.GET.get("search", ''),
            "developers" : profiles,
            "current_page": page_number,
        }
        
        if page_number and int(page_number) > paginator.num_pages:
            return {
                "message": "End of page."
            }
        
        
        return render(request, "users/our_developers.html", context)

    @staticmethod
    def view_profile(request, pk):
        
        profile = Profile.objects.get(id=pk)
        projects = profile.project_set.all()
        
        context = {"profile" : profile, "projects": projects, "view": True}
        return render(request, "users/account.html", context)

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    @login_required(login_url='login')
    def deleteSkill(request, pk):
        
        next = request.GET.get('next') or None
        
        skill = Skills.objects.get(id=pk)
        skill.delete()
        messages.error(request, f"Skill {skill.name} was deleted")
        if next:
            return redirect(next)
        return redirect("profile")

class Channel:

    @staticmethod
    def ChannelIDgenerator(user):
        
        channel_id = hashlib.md5(f"{uuid4()}".encode()).hexdigest()
        return channel_id
    
    @staticmethod
    def get_messages(user, chat_id):
        messages = Message.objects.filter(chat_id=chat_id)
        return messages
    
    @staticmethod
    def get_last_read_message_id(user, chat_id):
        
        last_message = Message.objects.filter(chat_id=chat_id).order_by('-sent_at').first()
        
        if not last_message:
            return None
        
        if last_message.sender == user:
            return last_message.id
        
        last_read_message = Message.objects.filter(chat_id=chat_id, is_read=True, receiver=user).order_by('-sent_at').first()
        if last_read_message:
            return last_read_message.id
        return None

    @staticmethod
    @login_required(login_url='login')
    def chat(request, chat_id):    
        socket_id = Channel.ChannelIDgenerator(user=request.user)
        try:
            opened_chat = UserView.get_user_profile_by_id(chat_id)
        except Profile.DoesNotExist:
            opened_chat = None
        
        members = [request.user, opened_chat.user]
        try:
            chat_record = ChatRecords.objects.filter(chat_members=request.user).filter(chat_members=opened_chat.user).distinct().first()
        except ChatRecords.DoesNotExist:
            chat_record = None
        
        if not chat_record:
            chat_record = ChatRecords.create_chat_record(members=members)
            
        chat_messages = Channel.get_messages(request.user, chat_id=chat_record.id)
        
        filtered_chats = [item for item in [
            {
                "id": chat.id,
                "members": [member for member in chat.chat_members.all() if member != request.user.profile.user],
            } for chat in request.user.chatrecords_set.all()
        ] if len(item.get("members")) > 0]
        
        for chat in filtered_chats:
            chat["unread_message_count"] = Message.objects.filter(receiver=request.user, is_read=False, chat_id=chat.get("id")).count()
            # chat["last_read_message_id"] = Channel.get_last_read_message_id(user=request.user, chat_id=chat_id)

        last_read_message_id = Channel.get_last_read_message_id(user=request.user, chat_id=chat_record.id)
        
        context = {
            "socket_id": socket_id,
            "chat_room_id": chat_record.id,
            "chat_messages": chat_messages,
            "opened_chat": opened_chat,
            "all_chats": filtered_chats,
            "last_read_message_id": last_read_message_id
        }        
        return render(request, "chat.html", context=context)
    
    @staticmethod
    @login_required(login_url='login')
    def chat_view(request, ):    
        
        socket_id = Channel.ChannelIDgenerator(user=request.user)
        
        filtered_chats = [item for item in [
            {
                "id": chat.id,
                "members": [member for member in chat.chat_members.all() if member != request.user.profile.user],
            } for chat in request.user.chatrecords_set.all()
        ] if len(item.get("members")) > 0]
        
        for chat in filtered_chats:
            chat["unread_message_count"] = Message.objects.filter(receiver=request.user, is_read=False, chat_id=chat.get("id")).count()

        
        context = {
            "chat_room_id": None,
            "all_chats": filtered_chats,
            "no_chat": True,
            "socket_id": socket_id,
        }        
        return render(request, "chat.html", context=context)