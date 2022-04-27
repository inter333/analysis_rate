from django.views.generic import TemplateView
from pip import main
from .forms import UrlForm
from django.shortcuts import redirect, render
from .mate import MateManager
from .models import *


class IndexView(TemplateView):
    def __init__(self):
        self.params = {
            'title': 'レート分析',
            'msg': 'マイページのURLを入力してください',
            'form': UrlForm()
        }

    def get(self, request):
        return render(request, 'personal_rate_analysis/index.html', self.params)

    def post(self, request):
        form = UrlForm(request.POST)
        if form.is_valid():
            url = request.POST["url"]
            mate_manager = MateManager()
            user_result,char_result = mate_manager.main(url)
            if not user_result:
                msg = "対戦データがありません"
                self.params = {
                    'title': '戦績',
                    'form': UrlForm(),
                    'msg' : msg,
                    'user_result' : user_result,
                    'char_result' : char_result,
                }
            else:
                self.params = {
                    'title': '戦績',
                    'form': UrlForm(),
                    'user_result' : user_result,
                    'char_result' : char_result,
                }
        else:
            self.params = {
            'title': 'レート分析',
            'form': UrlForm(),
            'error_message': '正しいURLを入力してください'

        }


        return render(request, 'personal_rate_analysis/index.html', self.params)
