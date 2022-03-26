from unittest import result
import bs4
import requests
import time
import re
import statistics
from .models import Fighter

def load_soup(link):
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML"," like Gecko) Version/8.0.7 Safari/600.7.12'
    url = link
    resp = requests.get( url , headers = {"User-Agent": ua} )  # WEBリクエスト
    resp.encoding = resp.apparent_encoding                            # 文字化け防止に文字コード指定
    soup = bs4.BeautifulSoup( resp.text, "html.parser" )              # 結果をsoupに格納
    return soup

def count_page(soup):
    page = soup.select('div.pageing ul.pagination li')
    if not page:
        page_count = 1
    else:
        page_count = int(page[-2].text)
    return page_count

def define_link(link,page_count):
    link = link+ "?page=" + str(page_count)
    return link

def extract_content(soup):
    div = soup.select('div.smash-row.mb-20')
    content = div[0].select('span.rate_text')
    char = div[0].select('div.row.row-center.va-middle.row-nomargin div.col-xs-8')
    return content,char

def extract_name(src):
    name = re.match("(.*icon/)(.*png)",str(src)).group(2)
    name = re.sub(".png","",name)
    return name

def update_result_dic(char_content,g_rate,dic):
    img = char_content.findAll('img', class_='smash-icon')
    for src in img:
        name = extract_name(src)
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

def add_rate_list(rate,g_rate,rate_list):
    if rate_list:
        rate = rate_list[-1]
    rate += g_rate
    rate_list.append(rate)
    return rate_list

def collect_late_information(rate_list,rate,chars,contents,dic):
    contents = reversed(contents)
    char_contents = reversed(chars)
    for content,char_content in zip(contents,char_contents):
        if "＋" in content.text:
            g_rate = int(content.text.replace("＋",""))
        elif "－" in content.text:
            g_rate = int(content.text.replace("－",""))
            g_rate = -g_rate
        else:
            pass
        rate_list = add_rate_list(rate,g_rate,rate_list)
        dic = update_result_dic(char_content,g_rate,dic)
    return rate_list,rate,dic

def analyze_rate(rate_list):
    l = []
    ave = sum(rate_list) / len(rate_list)
    print(len(rate_list))
    print(rate_list[-1])
    print(round(statistics.median(rate_list)))

    print(round(ave))
    print(max(rate_list))
    print(min(rate_list))
    l.append(len(rate_list))
    l.append(rate_list[-1])
    l.append(max(rate_list))
    l.append(min(rate_list))
    l.append(round(ave))
    l.append(round(statistics.median(rate_list)))
    return l

def analyze_battle_record(dic):
    fighteres = Fighter.objects.all()
    for x in fighteres:
        fighter = x.fighter_en
        try:
            if fighter in dic:
                print("ファイター")
                print(fighter)
                macht_num = len(dic[x.fighter_ja]["result"])
                print("試合数")
                print(macht_num)
                print("勝率")
                try:
                    win_rate = dic[fighter]["result"].count("勝ち") / macht_num * 100
                    print(round(win_rate))
                except ZeroDivisionError:
                    print(100)
        except KeyError:
            pass

def main(link):
    battle_record_dic = {}
    rate_list = []
    rate = 1500
    soup = load_soup(link)
    time.sleep(3)
    page_count = count_page(soup)
    print("レート取得中")
    while  page_count  != 0:
        new_link = define_link(link,page_count)
        new_soup = load_soup(new_link)
        div = new_soup.select('div.smash-row.mb-20')
        if div:
            content = div[0].select('span.rate_text')
            char_content = div[0].select('div.row.row-center.va-middle.row-nomargin div.col-xs-8')
            rate_list,rate,battle_record_dic = collect_late_information(rate_list,rate,char_content,content,battle_record_dic)
            page_count -= 1
            time.sleep(2)
        else:
            break

    print("レート取得完了")
    if rate_list:
        li = analyze_rate(rate_list)
        for x,y in battle_record_dic.items():
            win = int(y["record"].count("勝ち"))
            lose = int(y["record"].count("負け"))
            y["result"] = f"{win}勝{lose}敗"
        print(battle_record_dic)
        analyze_battle_record(battle_record_dic)
    else:
        li = ["対戦データがありません"]


    return li,battle_record_dic