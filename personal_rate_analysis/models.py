from django.db import models

class Fighter(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    fighter_ja = models.CharField(max_length=100)
    fighter_en = models.CharField(max_length=100)

class User(models.Model):
    mate_id = models.IntegerField(verbose_name='メイトID')
    user = models.CharField(max_length=255,verbose_name='ユーザー名')

    def __str__(self):
        return str(self.mate_id)

class UserResult(models.Model):
    span = models.FloatField(max_length=255,default='',verbose_name='期間')
    number_of_matches = models.IntegerField(default=0,verbose_name='試合数')
    last_rate = models.IntegerField(default=1500,verbose_name='最終レート')
    max_rate = models.IntegerField(default=1500,verbose_name='最高レート')
    min_rate = models.IntegerField(default=1500,verbose_name='最低レート')
    ave_rate = models.IntegerField(default=1500,verbose_name='平均レート')
    median_rate = models.IntegerField(default=1500,verbose_name='中央値')
    mate = models.ForeignKey(User, verbose_name='メイトID', on_delete=models.CASCADE)

    def __str__(self):
        return 'mate_id=' + str(self.mate) + ',span=' + str(self.span)

class CharResult(models.Model):
    fighter = models.CharField(max_length=255,default='',verbose_name='対戦したキャラ')
    number_of_matches = models.IntegerField(default=0,verbose_name='試合数')
    rate_balance = models.IntegerField(default=0,verbose_name='レート収支')
    results = models.CharField(max_length=100,default="",verbose_name='戦績')
    user_result = models.ForeignKey(UserResult, verbose_name='ユーザーデータ', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_result) + ',fighter=' +str(self.fighter)