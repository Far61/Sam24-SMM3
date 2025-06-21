import requests
from datetime import datetime, timedelta
import csv
import os
import config as conf

class VKStats:
    def __init__(self, vk_api_key, group_id):
        self.vk_api_key = vk_api_key
        self.group_id = group_id

    def get_group_id(self):
        url = 'https://api.vk.com/method/groups.getById'
        params = {
            'access_token': self.vk_api_key,
            'v': '5.131',
            'group_id': self.group_id
        }
        response = requests.get(url, params=params).json()
        return response['response'][0]['id']

    def get_stats(self, start_date, end_date):
        url = 'https://api.vk.com/method/stats.get'
        params = {
            'access_token': self.vk_api_key,
            'v': '5.131',
            'group_id': self.group_id,
            'date_from': start_date,
            'date_to': end_date
        }
        response = requests.get(url, params=params).json()
        if 'error' in response:
            raise Exception(response['error']['error_msg'])
        return response['response']

    def display_stats(self, stats):
        print("Дата\t\tПросмотры\tПосетители\tЛайки\tРепосты\tКомментарии\tПодписчики")
        for day_stats in stats:
            date = datetime.utcfromtimestamp(day_stats['period_from']).strftime('%Y-%m-%d')
            views = day_stats.get('views', 0)
            visitors = day_stats.get('visitors', 0)
            likes = day_stats.get('likes', 0)
            shares = day_stats.get('shares', 0)
            comments = day_stats.get('comments', 0)
            subscribers = day_stats.get('subscribed', 0) - day_stats.get('unsubscribed', 0)
            print(f"{date}\t{views}\t\t{visitors}\t\t{likes}\t{shares}\t{comments}\t\t{subscribers}")

    def save_stats_to_csv(self, stats, start_date, end_date):
        os.makedirs("output", exist_ok=True)

    # Формируем имя файла: vk_stats_2024-01-31_to_2024-05-30.csv
    filename = f"vk_stats_{start_date}_to_{end_date}.csv"
    filepath = os.path.join("output", filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Дата", "Просмотры", "Посетители", "Лайки", "Репосты", "Комментарии", "Подписчики"])

        for day_stats in stats:
            date = datetime.utcfromtimestamp(day_stats['period_from']).strftime('%Y-%m-%d')
            views = day_stats.get('views', 0)
            visitors = day_stats.get('visitors', 0)
            likes = day_stats.get('likes', 0)
            shares = day_stats.get('shares', 0)
            comments = day_stats.get('comments', 0)
            subscribers = day_stats.get('subscribed', 0) - day_stats.get('unsubscribed', 0)

            writer.writerow([date, views, visitors, likes, shares, comments, subscribers])

    print(f"📊 Статистика сохранена в файл: {filepath}")