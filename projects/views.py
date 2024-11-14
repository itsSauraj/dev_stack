import markdown
from bs4 import BeautifulSoup

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from .forms import ProjectForm, ReviewForm
from users.views import has_permission

from .models import Project, Tag, Review

from .filters import ProjectFilter

app_name = "projects"

def homepage(request):
    return render(request, f"{app_name}/home.html")


def projects(request):
    projects = Project.objects.all()
    
    md = markdown.Markdown(extensions=["fenced_code"])
        
    for project in projects:
        project.description = project.description[:200] + "..."
        soup = BeautifulSoup(md.convert(project.description), 'html.parser')
        project.description = soup.get_text()
    
    context = {
        "projects": projects,
    }
    return render(request, f"{app_name}/projects.html", context)

def project(request, pk):
    project = Project.objects.get(id=pk)
    projects = ProjectFilter({"creator__id": project.creator.id}, queryset=Project.objects.all())
        
    md = markdown.Markdown(extensions=["fenced_code"])
    project.description = md.convert(project.description)
    
    form = ReviewForm()
    
    reviews_queryset = project.reviews.all()
    
    total_rating = sum([review.get_review_stars() for review in reviews_queryset])
    average_rating = total_rating / len(reviews_queryset) if reviews_queryset else 0
    
    context = {
        "project": project,
        "projects": projects.qs,
        "reviews_from": form,
        "total_reviews": len(reviews_queryset),
        "average_rating": average_rating,
    }
    
    if request.method == "POST":
        
        form_data = request.POST.copy()
        form_data["project"] = project
        form_data["project__id"] = project.id
        
        form = ReviewForm(form_data)
        
        if form.is_valid():
            review = form.save()
            try:
                review.created_by = request.user.profile or None
            except:
                pass
            review.save()
            messages.success(request, "Review added successfully")
            return render(request, f"{app_name}/view_project.html", context=context)
        
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











def test(request, project_id):
    project = Project.objects.get(id=project_id)
    projects = ProjectFilter({"creator__id": project.creator.id}, queryset=Project.objects.all())
        
    md = markdown.Markdown(extensions=["fenced_code"])
    project.description = md.convert(project.description)
    
    form = ReviewForm()
    
    context = {
        "project": project,
        "projects": projects.qs,
        "reviews_from": form,
    }
    
    if request.method == "POST":
        
        form_data = request.POST.copy()
        form_data["project"] = project
        form_data["project__id"] = project.id
        
        form = ReviewForm(form_data)
        
        if form.is_valid():
            review = form.save()
            try:
                review.created_by = request.user.profile or None
            except:
                pass
            review.save()
            messages.success(request, "Review added successfully")
            return render(request, f"{app_name}/test.html", context=context)
        
    return render(request, f"{app_name}/test.html", context=context)