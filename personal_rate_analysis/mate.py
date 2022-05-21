from unittest import result
import bs4
import requests
import time
import re
import statistics
from .models import *

class MateManager:
    """スマメイトの対戦データを取得するクラス
    """
    def load_soup(self,link):
        """htmlを取得するメソッド

        bs4を用いて受け取ったurlからスマメイトのマイページに飛ぶ
        その後htmlを取得する

        Args:
            self:self
            link:スマメイトのマイページのurl
        Return:
            return:html情報
        """
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML"," like Gecko) Version/8.0.7 Safari/600.7.12'
        url = link
        resp = requests.get( url , headers = {"User-Agent": ua} )
        resp.encoding = resp.apparent_encoding
        soup = bs4.BeautifulSoup( resp.text, "html.parser" )
        return soup


    def update_char_result(self,char_content,g_rate,dic):
        """キャラごとの対戦結果をまとめるメソッド

        画像からキャラの情報を取得する
        その後既に情報があれば勝敗を更新
        なければ新規でデータを追加

        Args:
            self:self
            char_content:対戦相手のキャラ情報が入っているhtml情報
            g_ratet:取得したレート
            dic:キャラごとの対戦データが入っている辞書
        Return:
            return:キャラごとの対戦データが入っている辞書
        """
        img = char_content.findAll('img', class_='smash-icon')
        for src in img:
            name = re.match("(.*icon/)(.*png)",str(src)).group(2)
            name = re.sub(".png","",name)
            name = Fighter.objects.get(fighter_en=name)
            name = name.fighter_ja
            if "-" in str(g_rate):
                win_lose= "負け"
            else:
                win_lose = "勝ち"
            try:
                if dic[name]:
                    dic[name]["record"].append(win_lose)
                    dic[name]["total"] = dic[name]["total"] + g_rate
            except KeyError:
                dic[name] = {"record":[],"total":0}
                dic[name]["record"].append(win_lose)
                dic[name]["total"] = dic[name]["total"] + g_rate
        return dic

    def add_rate_list(self,rate,g_rate,rate_list):
        """個人の対戦データをリストに追加するメソッド

        取得したレートを計算したのち追加

        Args:
            self:self
            rate:既に取得しているレートの合計
            g_rate:取得したレート
            rate_list:既に取得したレートをまとめたリスト
        Return:
            return:既に取得したレートをまとめたリスト
        """

        if rate_list:
            rate = rate_list[-1]
        rate += g_rate
        rate_list.append(rate)
        return rate_list

    def operate_rate_information(self,rate_list,rate,chars,contents,dic,now_number_of_matches):
        """httmlからレートの収支を取得し各メソッドに渡すメソッド

        取得したレートをadd_rate_list,update_char_resultに渡す
        既にデータが登録されており、現在の試合数とその情報に差異があるときはその差だけ動く

        Args:
            self:self
            rate_list:既に取得したレートをまとめたリスト
            rate:既に取得しているレートの合計
            chars:対戦相手の情報が入ったhtml
            contents:レート収支の情報が入ったhtml
            dic:キャラごとの対戦データが入っている辞書
            now_number_of_matches:現在の総試合数
        Return:
            return:レート情報・キャラごと辞書・現在のレート
        """
        contents_count = len(contents)
        contents = reversed(contents)
        char_contents = reversed(chars)
        if now_number_of_matches < 20:
            increment = contents_count - now_number_of_matches
        else:
            increment = 0
        count = 1
        for content,char_content in zip(contents,char_contents):
            if count > increment:
                if "＋" in content.text:
                    g_rate = int(content.text.replace("＋",""))
                elif "－" in content.text:
                    g_rate = int(content.text.replace("－",""))
                    g_rate = -g_rate
                else:
                    g_rate = 0
                    count += 1
                    contents_count -= 1
                    continue
                rate_list = self.add_rate_list(rate,g_rate,rate_list)
                dic = self.update_char_result(char_content,g_rate,dic)
            count += 1
        return rate_list,rate,dic,contents_count

    def save_rate(self,rate_list,user_id,mate_id,span):
        """レートの情報を保存するメソッド

        取得したレートを各種計算し保存する

        Args:
            self:self
            rate_list:既に取得したレートをまとめたリスト
            user_id:外部キーを取得するためのid
            mate_id:UserResultのmate_id
            span:スマメイトの何期か
        """
        sum_games = len(rate_list)
        ave_rate = sum(rate_list) / sum_games
        max_rate = max(rate_list)
        min_rate = min(rate_list)
        last_rate = rate_list[-1]
        median_rate = round(statistics.median(rate_list))
        UserResult.objects.update_or_create(mate=mate_id,span=span,defaults={'number_of_matches':sum_games,'last_rate':last_rate,'max_rate':max_rate,'min_rate':min_rate,'ave_rate':ave_rate,'median_rate':median_rate,'mate':User.objects.get(id=user_id)})


    def main(self,link):
        """メイトの情報を取得し保存する一連のメインメソッド

        レートを取得しDBに保存するメインロジック
        既にすべての情報を取得している場合などはmodelの情報だけを返す
        情報を保存したのち、filterで該当する情報を持ってきてviewsに渡す

        Args:
            self:self
            link:スマメイトのurl
        Return:
            return:レート情報,対戦キャラごとのデータ
        """
        battle_record_dic = {}
        rate_list = []
        rate = 1500
        span = 19
        soup = self.load_soup(link)
        time.sleep(3)

        #一度も対戦していない可能性を考えての条件分岐

        now_number_of_matches = soup.select('div.col-xs-4 div.row.row-center.va-middle div.col-xs-6')
        if not now_number_of_matches:
            user_result,char_result = "",""
            return user_result,char_result

        #最新の試合数・メイトIDを取得

        now_number_of_matches = now_number_of_matches[5].text
        now_number_of_matches = re.sub(r"[ \t\n敗]", "", now_number_of_matches)
        now_number_of_matches = now_number_of_matches.split(('勝'))
        if '現在' in now_number_of_matches[1]:
            now_number_of_matches[1] = re.match("(.*現在)",now_number_of_matches[1]).group(1)
            now_number_of_matches[1] = re.sub("現在","",now_number_of_matches[1])
        now_number_of_matches = int(now_number_of_matches[0]) + int(now_number_of_matches[1])
        #now_number_of_matches = now_number_of_matches[0]

        mate_id = re.sub(r"\D", "", link)
        user_obj = User.objects.filter(mate_id=mate_id).values()
        user_name = soup.select('div.side.user-data span.user-name')
        user_name = user_name[0].text

        #既に対戦データがあるか・差分だけ取るのか・すべて取得するのか

        if (user_obj) and (user_obj[0]["id"]):
            mate_id = user_obj[0]["id"]
            user_result_obj = UserResult.objects.filter(mate_id=mate_id,span=span).values()
            if (user_result_obj) and user_result_obj[0]["id"]:
                user_id = user_result_obj[0]["id"]
                number_of_matches = user_result_obj[0]["number_of_matches"]
                if now_number_of_matches != number_of_matches:
                    now_number_of_matches = number_of_matches - now_number_of_matches
                else:
                    user_result = UserResult.objects.filter(mate_id=mate_id,span=span).values()[0]
                    char_result = CharResult.objects.filter(user_result_id=user_result["id"]).order_by("-rate_balance")
                    return user_result,char_result
            else:
                user_id = user_obj[0]["id"]
        else:
            mate_id = re.sub(r"\D", "", link)
            user_id = User.objects.create(mate_id=mate_id,user=user_name)
            user_id = user_id.id

        page = soup.select('div.pageing ul.pagination li')
        page_count = int(page[-2].text)
        if not page:
            page_count = 1
        else:
            page_count = int(page[-2].text)


        #対戦データを取得するループ

        while  now_number_of_matches  != 0:
            new_link = link + "?page=" + str(page_count)
            new_soup = self.load_soup(new_link)
            div = new_soup.select('div.smash-row.mb-20')
            if div:
                content = div[0].select('span.rate_text')
                char_content = div[0].select('div.row.row-center.va-middle.row-nomargin div.col-xs-8')
                rate_list,rate,battle_record_dic,contens_count = self.operate_rate_information(rate_list,rate,char_content,content,battle_record_dic,now_number_of_matches)
                now_number_of_matches -= contens_count
                page_count -= 1
                time.sleep(2)

        #取得したデータをDBにいれる

        self.save_rate(rate_list,user_id,mate_id,span)
        user_result = UserResult.objects.filter(mate_id=user_id,span=span).values()[0]
        for fighter,y in battle_record_dic.items():
            win = int(y["record"].count("勝ち"))
            lose = int(y["record"].count("負け"))
            y["result"] = f"{win}勝{lose}敗"
            CharResult.objects.update_or_create(user_result=UserResult.objects.get(mate_id=user_id,span=span),fighter=fighter,defaults={'fighter':fighter,'number_of_matches':win+lose,'rate_balance':y['total'],'results':y["result"]})
        char_result = CharResult.objects.filter(user_result_id=user_result["id"]).order_by("-rate_balance")
        return user_result,char_result