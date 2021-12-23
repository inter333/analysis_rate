from django.views.generic import TemplateView
from .forms import UrlForm
from django.shortcuts import render
from .mate import main


class IndexView(TemplateView):
    def __init__(self):
        self.params = {
            'title': 'Hello',
            'message': 'your data',
            'form': UrlForm()
        }

    def get(self, request):
        return render(request, 'index.html', self.params)

    def post(self, request):
        url = request.POST["url"]
        main(url)

        self.params['message'] = url
        self.params['form'] = UrlForm(request.POST)

        return render(request, 'index.html', self.params)
