import requests
import pandas as pd
import os.path


class CyberLeninka(object):
    url = 'https://cyberleninka.ru'
    api_url = 'https://cyberleninka.ru/api/search'
    file_path = './cyberleninka.csv'

    @staticmethod
    def get_url_request(request, page=1):
        return CyberLeninka.url.format(request, page)

    @staticmethod
    def request(request, size=10, fromItem=0):
        return requests.post(CyberLeninka.api_url, json={
            "mode": "articles",
            "q": request,
            "size": size,
            "from": fromItem
        }).json()

    @staticmethod
    def fetch_articles(request, size=10, fromItem=0):
        data = CyberLeninka.request(request, size, fromItem)
        if not data or not data['articles']:
            return []
        return [{
            'source': 'CyberLeninka',
            'title': data['articles'][i]['name'],
            'link': CyberLeninka.url + data['articles'][i]['link'],
            'authors': ', '.join(data['articles'][i]['authors']),
        } for i in range(size)]

    @staticmethod
    def fetch_df(request, size=10, fromItem=0):
        return pd.DataFrame(CyberLeninka.fetch_articles(request, size, fromItem))

    @staticmethod
    def fetch_df_cached(request, size=10, fromItem=0, refresh=False):
        if not refresh and os.path.exists(CyberLeninka.file_path):
            try:
                df = pd.read_csv(CyberLeninka.file_path)
                if df.shape[0] == size:
                    return df
            except:
                pass

        df = CyberLeninka.fetch_df(request, size, fromItem)
        if df.shape[0] != 0:
            df.to_csv(CyberLeninka.file_path, index=False)
        return df

    @staticmethod
    def save_df(df):
        df.to_csv(CyberLeninka.file_path, index=False)
