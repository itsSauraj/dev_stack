from django.shortcuts import render, redirect, HttpResponse
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
            return render(request, "users/login_register.html", {"error": "User does not exist"})
        
        if user.check_password(password) == False:
            return render(request, "users/login_register.html", {"error": "Incorrect password"})
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            if next is not None:
                return redirect(next)
            
            return redirect('profile')
        else:
            return render(request, "users/login_register.html", {"error": "something went wrong", 'user': user})
			
    
    return render(request, "users/login_register.html")


def logout_user(request):
    logout(request)
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
            return redirect('login')
    
    return render(request, "users/login_register.html", {'page': page, 'form': form})

@login_required(login_url='login')
def delete_user(request):
    
    username = request.user.username
    typed = request.POST.get("username")
    
    user = request.user
    
    print( username, typed)
    
    if username != typed:
        #TODO: add error message
        return HttpResponse("Incorrect username")
    user.delete()
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
        return redirect("profile")
    
    context =  {"profile": profile, "form": form}
    return render(request, "users/skill_form.html", context)

@login_required(login_url='login')
def updateSkill(request, pk):
    
    skill = Skills.objects.get(id=pk)
    form = SkillForm(instance=skill)
    
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
        return redirect("profile")
    
    context =  {"profile": skill.profile, "form": form, "page": "update", "skill": skill}
    return render(request, "users/skill_form.html", context)

@login_required(login_url='login')
def deleteSkill(request, pk):
    
    next = request.GET.get('next') or None
    
    skill = Skills.objects.get(id=pk)
    skill.delete()
    if next:
        return redirect(next)
    return redirect("profile")