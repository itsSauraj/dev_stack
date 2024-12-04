from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect

from projects.forms import ProjectForm
from users.views import UserView

from projects.models import Project, Tag


from .services.reviews import ReviewService
from .services.projects import ProjectService

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

app_name = "projects"
has_permission = UserView.has_permission

def homepage(request):
    return render(request, f"{app_name}/home.html")

class ProjectsView:
    def projects(request):
        search_query = {'search': request.GET.get("search")}
        page_number = request.GET.get('page')
                
        projects = ProjectService.get_projects(search_query=search_query)

        paginator = Paginator(projects, 25)
        projects = paginator.get_page(page_number)
        
        context = {
            'search_query': request.GET.get("search", ''),
            "projects": projects,
            "total_pages": paginator.num_pages,
            "current_page": page_number,
        }
        
        if page_number and int(page_number) > paginator.num_pages:
            return {
                "message": "End of page."
            }
        
        return render(request, f"{app_name}/projects.html", context)

    def project(request, pk):
        project = ProjectService.get_project_by_id(pk)
        creator_projects = ProjectService.get_creator_projects(creator_id=project.creator.id, limit=5)
                
        project_reviews = ReviewService.get_reviews(project)
        average_rating = ReviewService.average_rating(project)
        
        context = {
            "project": project,
            "projects": creator_projects,
            "total_reviews": len(project_reviews),
            "average_rating": average_rating,
        }
        
        return render(request, f"{app_name}/view_project.html", context=context)


    @login_required(login_url="/user/login/")
    def create_project(request):
        form = ProjectForm()
        next = request.GET.get("next")
        if request.method == "POST":
            form = ProjectForm(request.POST, request.FILES)
            ProjectService.create(request, form)
            if next:
                return redirect(next)
            return redirect("projects")
            
        context = {
            "form": form
        }
        if next:
            context["next"] = next
        return render(request, f"{app_name}/project_form.html", context)

    @login_required(login_url="/user/login/")
    @has_permission
    def update_project(request, pk):
        next = request.GET.get("next") or None
        
        project = ProjectService.get_project_by_id(pk)
        
        form = ProjectForm(instance=project)
        
        if request.method == "POST":
            form = ProjectForm(request.POST, request.FILES, instance=project)
            ProjectService.update(request, form)
            
            if next:
                return redirect(next)
            return redirect("projects")
        
        context = {
            "form": form,
            "update": True,
            "project": project
        }
        return render(request, f"{app_name}/project_form.html", context)


    @login_required(login_url="/user/login/")
    @has_permission
    def delete_project(request, pk):
        
        next = request.GET.get("next") or None
        
        if request.method == "POST":
            
            project = Project.objects.get(id=pk)
            if request.method == "POST":
                ProjectService.delete(request, project)
                messages.error(request, "Project deleted successfully")
                if next:
                    return redirect(next)
                return redirect("projects")
        else:
            return JsonResponse({"error": "Bad Request"}, status=400)   
        return JsonResponse({"error": "Bad Request"}, status=400)