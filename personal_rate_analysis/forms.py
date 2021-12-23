from django import forms

class UrlForm(forms.Form):
    url = forms.URLField(max_length=100, required=True,
                              widget=forms.TextInput(
                                   attrs={'placeholder': 'https://smashmate.net/user/66913/'}))