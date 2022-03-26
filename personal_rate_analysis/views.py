from django.views.generic import TemplateView
from .forms import UrlForm
from django.shortcuts import redirect, render
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
        print(url)
        li,dic = main(url)

        self.params = {
            'title': '戦績',
            'form': UrlForm(),
            'msg' : '取得した',
            'results' : li,
            'dic' : dic,
        }

        return render(request, 'index.html', self.params)
