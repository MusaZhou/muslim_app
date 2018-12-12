from django import forms
from management import choices

class SearchForm(forms.Form):
    search_key = forms.CharField(max_length=100)
    search_type = forms.ChoiceField(choices=choices.SEARCH_TYPE_CHOICES)