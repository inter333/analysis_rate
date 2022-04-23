from django import forms
import re

class UrlForm(forms.Form):
    url = forms.URLField(max_length=100, required=True,
                              widget=forms.TextInput(
                                   attrs={'placeholder': 'https://smashmate.net/user/66913/'}))

    def clean_url(self):
        url = self.cleaned_data['url']
        mate_id = re.sub(r"\D", "", url)
        if 'smashmate.net' not in url or len(mate_id) != 5:
            raise forms.ValidationError('urlが正しくありません')
        return url