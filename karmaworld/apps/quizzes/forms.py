from django import forms
from django.forms import TextInput, Textarea


class KeywordForm(forms.Form):
    keyword = forms.CharField(widget=TextInput)
    definition = forms.CharField(widget=Textarea)
    id = forms.IntegerField(required=False)

    def as_p(self):
        return '<div class="row keyword-form-row"><div class="small-4 columns">' + \
                self['keyword'].as_text(attrs={'placeholder': 'Keyword', 'class': 'keyword'}) + \
                '</div><div class="small-8 columns">' + \
                self['definition'].as_textarea(attrs={'placeholder': 'Definition', 'class': 'definition'}) + \
                self['id'].as_hidden(attrs={'class': 'object-id'}) + \
                '</div></div>'

