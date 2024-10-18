from django.forms import ModelForm, CheckboxSelectMultiple, TextInput, Textarea


from .models import Project


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        exclude = ['id', 'created_at', 'updated_at', 'deleted_at', 'creator', 'tags']        
        widgets = {
            'title': TextInput(
              attrs={
                'placeholder': 'Title'
              }),
            'description': Textarea(
              attrs={
                'placeholder': 'Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of class....'
              }),
            'demo_link': TextInput(
              attrs={
                'placeholder': 'https://example.com'
              }),
            'source_link': TextInput(
              attrs={
                'placeholder': 'https://example.com'
              }),
        }
        
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input input--text'})

