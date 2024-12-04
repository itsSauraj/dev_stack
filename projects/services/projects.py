import markdown
from bs4 import BeautifulSoup

from django.contrib import messages

from projects.filters import ProjectSearchFilter

from projects.models import Project, Tag
from projects.dependencies.project import clean_tags

class ProjectService:

    @staticmethod
    def get_project_by_id(pk):
        return Project.objects.get(id=pk)
    
    @staticmethod
    def get_user_projects(pk):
        projects = Project.objects.filter(creator__id=pk)
        return projects
    
    @staticmethod
    def get_projects(search_query):
        
        searched_projects  = ProjectSearchFilter(search_query, queryset=Project.objects.all())
        projects = searched_projects.qs
        
        projects = Project.objects.all()
        projects = ProjectService.parse_description_html(projects, many=True)
        
        return projects
    
    @staticmethod
    def get_creator_projects(creator_id, limit=None):
        projects = Project.objects.filter(creator__id=creator_id).order_by('-created_at')
        if limit:
            projects = projects[:limit]
        return projects
    
    @staticmethod
    def parse_description_html(project, many=False):
        
        if many:
            for proj in project:
                proj.description = ProjectService.__parse_html(proj.description)
            return project
            
        project.description = ProjectService.__parse_html(project.description)
        return project
            
    @staticmethod
    def __parse_html(htmlx):
        md = markdown.Markdown(extensions=["fenced_code"])
        soup = BeautifulSoup(md.convert(htmlx), 'html.parser')
        text = soup.get_text()
        if len(text) > 200:
            return text[:200] + "..."
        return text
    
    @staticmethod
    def create(request, form):

        tags = clean_tags(request.POST.get("tags"))

        if form.is_valid():
            project = form.save()
            project.creator = request.user.profile
            project.save()

            ProjectService.update_project_tags(request, project, tags)
            messages.success(request, "Project created successfully")
        
    @staticmethod
    def update(request, form):

        tags = clean_tags(request.POST.get("tags"))

        if form.is_valid():
            project = form.save()

            ProjectService.update_project_tags(request, project, tags)
            messages.success(request, "Project updated successfully")
    
    @staticmethod
    def update_project_tags(request, project, tags):    
        for tag in project.tags.all():
            project.tags.remove(tag)
        
        for tag in tags:
            tag, created = Tag.objects.get_or_create(name=tag, defaults={'creator': request.user.profile})
            project.tags.add(tag)
            

    @staticmethod
    def delete(request, project):
        project.delete()
        messages.success(request, "Project deleted successfully")