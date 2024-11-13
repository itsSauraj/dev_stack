import markdown

import django_filters

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from .forms import ProjectForm
from users.views import has_permission

from .models import Project, Tag

from .filters import ProjectFilter

app_name = "projects"

def homepage(request):
    return render(request, f"{app_name}/home.html")


def projects(request):
    projects = Project.objects.all()    
    context = {
        "projects": projects,
    }
    return render(request, f"{app_name}/projects.html", context)

def project(request, pk):
    project = Project.objects.get(id=pk)
    
    projects = ProjectFilter({"creator__id": project.creator.id}, queryset=Project.objects.all())
        
    md = markdown.Markdown(extensions=["fenced_code"])
    project.description = md.convert(project.description)
    
    context = {
        "project": project,
        "projects": projects.qs
    }
    return render(request, f"{app_name}/view_project.html", context=context)


@login_required(login_url="/user/login/")
def create_project(request):
    form = ProjectForm()
    next = request.GET.get("next")
    if request.method == "POST":
        
        tags_string = request.POST.get("tags")
        tags = tags_string.split(",")
        tags = [tag.strip() for tag in tags if len(tag.strip()) > 0]
        
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            project.creator = request.user.profile
            project.save()
        
            for tag in project.tags.all():
                project.tags.remove(tag)
            
            for tag in tags:
                tag, created = Tag.objects.get_or_create(name=tag, defaults={'creator': request.user.profile})
                project.tags.add(tag)
                
            messages.success(request, "Project created successfully")
            if next:
                return redirect(next)
            return redirect("projects")
        
    context = {
        "form": form
    }
    if next:
        context["next"] = next
    return render(request, f"{app_name}/create_project.html", context)


@login_required(login_url="/user/login/")
def update_project(request, pk):

    if not has_permission(request.user.profile, pk):
        return redirect("developer", pk=request.user.profile.id)
    
    next = request.GET.get("next") or None
    
    project = Project.objects.get(id=pk)
    form = ProjectForm(instance=project)
    if request.method == "POST":
        
        tags_string = request.POST.get("tags")
        tags = tags_string.split(",")
        tags = [tag.strip() for tag in tags if len(tag.strip()) > 0]

        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save()
        
            for tag in project.tags.all():
                project.tags.remove(tag)
            
            for tag in tags:
                tag, created = Tag.objects.get_or_create(name=tag, defaults={'creator': request.user.profile})
                project.tags.add(tag)
            
            messages.success(request, "Project updated successfully")
            if next:
                return redirect(next)
            return redirect("projects")
    context = {
        "form": form,
        "update": True,
        "project": project
    }
    return render(request, f"{app_name}/create_project.html", context,)


@login_required(login_url="/user/login/")
def delete_project(request):
    if not has_permission(request.user.profile, pk):
        return redirect("developer", pk=request.user.profile.id)
    
    
    next = request.GET.get("next") or None
    
    if request.method == "POST":
        pk = request.POST.get("pk")
        
        project = Project.objects.get(id=pk)
        if request.method == "POST":
            project.delete()
            messages.error(request, "Project deleted successfully")
            if next:
                return redirect(next)
            return redirect("projects")
    else:
        return JsonResponse({"error": "Bad Request"}, status=400)   
    return JsonResponse({"error": "Bad Request"}, status=400)
