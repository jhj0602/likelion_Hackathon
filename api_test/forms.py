from django import forms
from myapp.models import itemsaved

class MediaForm(forms.ModelForm):
    class Meta:
        model = itemsaved
        fields = ['image']
    