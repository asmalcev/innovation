import bs4
import requests
import pandas as pd
import os.path


class Habr(object):
    host = 'https://habr.com'
    url = 'https://habr.com/ru/search/page{}/?q={}&target_type=posts&order=relevance'
    file_path = './habr.csv'

    @staticmethod
    def request(request, page=1):
        response = requests.get(Habr.url.format(page, request))

        if response.status_code != 200:
            print('ERROR', response)
            return None

        return response

    @staticmethod
    def request_soup(request, page=1):
        response = Habr.request(request, page)

        if not response:
            return None

        try:
            soup = bs4.BeautifulSoup(response.text, features="lxml")
        except:
            return None

        return soup

    @staticmethod
    def request_articles(request, page=1):
        soup = Habr.request_soup(request, page)

        if not soup:
            return []

        data = {}
        data['authors'] = list(map(lambda a: a.getText().replace('\n', ''), soup.select('.tm-user-info__username')))
        data['titles'] = list(map(lambda a: a.getText(), soup.select('.tm-title__link')))
        data['links'] = list(map(lambda a: Habr.host + a['href'], soup.select('.tm-title__link')))

        return [{
            'source': 'Habr',
            'title': data['titles'][i],
            'link': data['links'][i],
            'authors': data['authors'][i],
        } for i in range(len(data['titles']))]

    @staticmethod
    def fetch_articles(request, pages=1):
        articles = []

        for p in range(pages):
            response = Habr.request_articles(request, p + 1)
            if len(response) == 0:
                break
            articles += response

        return articles

    @staticmethod
    def fetch_df(request, pages=1):
        return pd.DataFrame(Habr.fetch_articles(request, pages))

    @staticmethod
    def fetch_df_cached(request, pages=1, refresh=False):
        if not refresh and os.path.exists(Habr.file_path):
            try:
                df = pd.read_csv(Habr.file_path)
                return df
            except:
                pass

        df = Habr.fetch_df(request, pages)
        if df.shape[0] != 0:
            df.to_csv(Habr.file_path, index=False)
        return df
