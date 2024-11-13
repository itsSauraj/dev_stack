from django.shortcuts import render, redirect, HttpResponse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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
        return HttpResponse("Incorrect username")
    user.delete()
    messages.error(request, "We are sad to loose you " + username)
    return redirect('login')


@login_required(login_url='login')
def profile(request):
    
    pk = request.user.profile.id
    
    profile = Profile.objects.get(id=pk)
    user = profile.user
    
    if user != request.user:
        return redirect("developer-view", pk=pk)
    
    projects = profile.project_set.all()
    
    context = {"profile" : profile , "projects": projects}
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
    user = profile.user
    
    projects = profile.project_set.all()
    
    context = { "user": user,"profile" : profile , "projects": projects, "view": True}
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