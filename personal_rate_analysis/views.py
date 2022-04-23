from django.views.generic import TemplateView
from .forms import UrlForm
from django.shortcuts import redirect, render
from .mate import main


class IndexView(TemplateView):
    def __init__(self):
        self.params = {
            'title': 'レート分析',
            'form': UrlForm()
        }

    def get(self, request):
        return render(request, 'personal_rate_analysis/index.html', self.params)

    def post(self, request):
        form = UrlForm(request.POST)
        if form.is_valid():
            url = request.POST["url"]
            li,dic = main(url)

            self.params = {
                'title': '戦績',
                'form': UrlForm(),
                'msg' : '取得結果',
                'results' : li,
                'dic' : dic,
            }
        else:
            self.params = {
            'title': 'レート分析',
            'form': UrlForm(),
            'error_message': '正しいURLを入力してください'

        }


        return render(request, 'personal_rate_analysis/index.html', self.params)
