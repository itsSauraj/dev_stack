from django.forms import ModelForm, TextInput, Textarea, Select


from .models import Project, Review


class   ProjectForm(ModelForm):
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
            


class ReviewForm(ModelForm):
    global NUMBER_CHOICES
    NUMBER_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    class Meta:
        model = Review
        fields = ['body', 'value', 'project']
        
        widgets = {
            'body': Textarea(
              attrs={
                'placeholder': 'Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of class....',
                'rows': 2
              }), 
            'value': Select(choices=NUMBER_CHOICES)
        }

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input input--text'})