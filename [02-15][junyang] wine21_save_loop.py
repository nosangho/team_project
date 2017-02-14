from collections import OrderedDict
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

df = pd.read_csv('pd_url_list_short.csv')       #df 변수로 csv 파일을 읽어옵니다.

#기존에 수동으로 입력하던 크롤링 범위를 start와 end로 지정해줬습니다.(클래스 만들때 입력)
class GetText(object):
    def __init__(self, ulist, start, end):                  #나중에 ulist 부분에는 앞에서 정의한 df를 넣어줍니다.
        self.ulist = ulist
        self.start = start
        self.end = end

    def wine_info(self):                        #wine_dict는 id, name, production 등등을 key로 갖는 사전.
        wine_dict = OrderedDict()               # 각각의 key는 리스트를 value로 갖습니다.
        wine_dict['id'] = []
        wine_dict['name'] = []
        wine_dict['production1'] = []
        wine_dict['production2'] = []
        wine_dict['production3'] = []
        wine_dict['production4'] = []
        wine_dict['type'] = []
        wine_dict['alc'] = []
        wine_dict['producer'] = []
        wine_dict['varieties'] = []
        wine_dict['bestfor'] = []
        wine_dict['sweetness'] = []
        wine_dict['body'] = []
        wine_dict['tastingnote'] = []

        for i in range(self.start, self.end):                  # 크롤링할 범위 설정(wine_code가 아니라 인덱스 번호)
            url = self.ulist.iloc[i]['URL']          # self.ulist가 dataframe 형식이므로 iloc 이용해서 url을 가져옵니다.
            res = requests.get(url)
            soup = BeautifulSoup(res.content)

            idnum = re.search(r'\d{5}', url).group()    #wine_code부터 크롤링 시작
            wine_dict['id'].append(idnum)

            try:
                li0 = soup.find('li', attrs = {'class' : 'WineEndName'})   #예외처리 해줄 것
                wine_name = li0.get_text()
                wine_dict['name'].append(wine_name)
            except:
                wine_dict['name'].append('None')

            try:
                li1 = soup.find('li', attrs = {'class' : 'WineProduction'})
                a = li1.find_all('a')
                for i in range(4):
                    if i <= len(a) -1 :
                        wine_dict['production{}'.format(i+1)].append(a[i].get_text())
                    else :
                        wine_dict['production{}'.format(i+1)].append('None')
            except:
                wine_dict['production1'].append('None')
                wine_dict['production2'].append('None')
                wine_dict['production3'].append('None')
                wine_dict['production4'].append('None')

            try:
                li1_1 = soup.find('li', attrs = {'class' : 'WineInfo'})
                words = li1_1.get_text().strip()
                wine_dict['type'].append(re.search(r'^\w+', words).group())
            except:
                wine_dict['type'].append('None')

            try:
                li = soup.find('li', attrs = {'class' : 'WineInfo'})
                aic = re.search(r'AIC[.\d]+', li.get_text().strip())
                if not aic :
                    wine_dict['alc'].append('None')
                else :
                    wine_dict['alc'].append(aic.group())
            except:
                wine_dict['alc'].append('None')

            try:
                li2 = soup.find('li', attrs = {'class' : 'Winery'})
                producer = li2.a.get_text()
                reproducer = re.sub(r'\s', ' ', producer)
                wine_dict['producer'].append(reproducer)
            except:
                wine_dict['producer'].append('None')

            try:
                li3 = soup.find('li', attrs = {'class' : 'Varieties'})
                varieties = ''
                for var in li3.find_all('a') :
                    varieties += var.get_text()
                wine_dict['varieties'].append(varieties)
            except:
                wine_dict['varieties'].append('None')

            try:
                li4 = soup.find('li', attrs = {'class' : 'BestFor'})
                bestfor = li4.get_text()
                wine_dict['bestfor'].append(bestfor.strip())
            except:
                wine_dict['bestfor'].append('None')


            try :
                li6 = soup.find('li', attrs = {'class' : 'Sweetness'})
                px = li6.find_all('img')[1]['style']
                wine_dict['sweetness'].append(re.search(r'\d+', px).group())
            except :
                wine_dict['sweetness'].append('None')

            try :
                li7 = soup.find('li', attrs = {'class' : 'Body'})
                px = li7.find_all('img')[1]['style']
                wine_dict['body'].append(re.search(r'\d+', px).group())
            except :
                wine_dict['body'].append('None')

            try:
                ul = soup.find('ul', attrs = {'class' : 'TastingnoteList'})
                note = ul.get_text().strip()
                subnote = re.sub(r'\s', ' ', note)             #정규표현식으로 \s(공백?)을 그냥 띄어쓰기로 바꿔줬습니다.
                wine_dict['tastingnote'].append(subnote)       #(\s 형식 중에 공백이 아닌 문자도 있던데 그부분이 저장시
            except:                                            #문제를 일으키는것 같아서요)
                wine_dict['tastingnote'].append('None')

        wine_df = pd.DataFrame(wine_dict)           # 사전 형식의 wine_dict를 dataframe 형식의 wine_df로 바꿔줍니다.

        return wine_df

#엑셀로 저장하는 것이 문제이므로 500개씩 저장을 시도하고 오류가 나면 다음 500개를 저장하게 코드를 짰습니다.
#0~4000번째까지 긁는 코드입니다.
i=0
while i<4000:
    wine2 = GetText(df,i,i+500)             # 시작과 끝이 루프를 돌 때마다 변하게 설정
    result = wine2.wine_info()
    try:
        writer = pd.ExcelWriter('./wine{}_{}.xlsx'.format(i,i+500), engine=None)  #파일 이름도 자동으로 변경하게 설정
        result.to_excel(writer, sheet_name='1', encoding ='utf-8')      # 결과를 엑셀로 저장
        writer.save()
        i += 500   #500개를 크롤링 후 저장을 끝내면 i가 500씩 증가
    except:
        i += 500   #오류가 나면 바로 i가 500만큼 증가해서 다음 500개에 대한 크롤링을 진행합니다.
        continue
