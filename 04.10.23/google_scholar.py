import bs4
import requests
import pandas as pd
import os.path


class GoogleScholar(object):
    url = 'https://scholar.google.com/scholar?start={}&q={}'
    file_path = './googlescholar.csv'

    @staticmethod
    def request(request, page=0):
        response = requests.get(GoogleScholar.url.format(page * 10, request))

        if response.status_code != 200:
            print('ERROR', response)
            return None

        return response

    @staticmethod
    def request_soup(request, page=0):
        response = GoogleScholar.request(request, page)

        if not response:
            return None

        try:
            soup = bs4.BeautifulSoup(response.text, features="lxml")
        except:
            return None

        return soup

    @staticmethod
    def request_articles(request, page=0):
        soup = GoogleScholar.request_soup(request, page)

        if not soup:
            return []

        data = {}
        data['titles'] = soup.select('.gs_rt a')
        data['authors'] = soup.select('.gs_a')

        return [{
            'source': 'GoogleScholar',
            'title': data['titles'][i].getText(),
            'link': data['titles'][i]['href'],
            'authors': ', '.join(map(lambda au: au.getText(), data['authors'][i].select('a'))),
        } for i in range(len(data['titles']))]

    @staticmethod
    def fetch_articles(request, pages=1):
        articles = []

        for p in range(pages):
            response = GoogleScholar.request_articles(request, p)
            if len(response) == 0:
                break
            articles += response

        return articles

    @staticmethod
    def fetch_df(request, pages=1):
        return pd.DataFrame(GoogleScholar.fetch_articles(request, pages))

    @staticmethod
    def fetch_df_cached(request, pages=1, refresh=False):
        if not refresh and os.path.exists(GoogleScholar.file_path):
            try:
                df = pd.read_csv(GoogleScholar.file_path)
                return df
            except:
                pass

        df = GoogleScholar.fetch_df(request, pages)
        if df.shape[0] != 0:
            df.to_csv(GoogleScholar.file_path, index=False)
        return df
