from datetime import datetime, timezone
import time
import pandas as pd
import requests

access_token = "vk1.a.nuXxpclU0Gc3koMcFE1cnRztIKJD7nUvR-B5JboHTwV_XdoOIm99795ubTdhwsO29bqiKG6DtrjiWH3sc4FgEBNtn8XeBHUprMLmwKyONAjbEvM3OeXxhgB-GE9SkffucUekrj7iy5wSrSPWgo1ZN3d-1n1_Xmiw05IqvSTxVBP4sifkPHz5PTTNfsiHop1iTcW8auAXkKOZvsSiSrsSIg"
url_start = "https://vk.com/kinocube_official"
url = url_start.split('/')
domain = url[-1]

# Получаем id группы через запрос
response = requests.get('https://api.vk.com/method/utils.resolveScreenName',
                        params={'access_token': access_token,
                                'screen_name': domain,
                                'v': 5.199})
id_group = response.json()['response']['object_id']


def fetch_vk_data(access_token, version=5.199, count=100, offset=0):
    # Словарь для хранения данных постов
    data_dict = {
        'ID': [],
        'Text': [],
        'Likes': [],
        'Comments': [],
        'Views': [],
        'Reposts': [],
        'URL': [],
        'Date': [],
        'Date_UNIX': [],
        'Photo': []
    }

    # Получение постов из группы
    while True:
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={'access_token': access_token,
                                        'v': version,
                                        'domain': domain,
                                        'count': count,
                                        'offset': offset})
        data_start = response.json()
        
        # Если нет постов, выходим из цикла
        if 'response' not in data_start or len(data_start['response']['items']) == 0:
            break

        data = data_start['response']['items']
        data_dict['ID'].extend([item['id'] for item in data])
        data_dict['Likes'].extend([item['likes']['count'] for item in data])
        data_dict['Text'].extend([item['text'] for item in data])
        data_dict['Comments'].extend([item['comments']['count'] for item in data])
        data_dict['Views'].extend([item.get('views', {}).get('count', None) for item in data])
        data_dict['Reposts'].extend([item['reposts']['count'] for item in data])
        data_dict['URL'].extend([f"{url_start}?w=wall-{id_group}_{item['id']}" for item in data])
        data_dict['Date'].extend([datetime.fromtimestamp(item['date'], timezone.utc).strftime('%Y-%m-%d') for item in data])
        data_dict['Date_UNIX'].extend([item['date'] for item in data])
        data_dict['Photo'].extend([item['attachments'][0]['photo']['sizes'][-1]['url'] if 'attachments' in item and item['attachments'] and item['attachments'][0]['type'] == 'photo' else "No photo" for item in data])

        # Увеличиваем смещение
        offset += len(data)
        time.sleep(0.01)

    df_posts = pd.DataFrame(data_dict)
    return df_posts

# Парсинг постов
df = fetch_vk_data(access_token, version=5.199, count=100, offset=0)

# Начальное и конечное время
start_time = '1672562957'  # Это можно заменить на df['Date_UNIX'].iloc[-1] + 10000, если нужно
end_time = str(int(datetime.now().timestamp()))

def fetch_vk_stats(start_time, end_time, access_token, id_group):
    # Загрузка всех параметров
    params = {
        'access_token': access_token,
        'group_id': id_group,
        'timestamp_from': start_time,
        'timestamp_to': end_time,
        'v': 5.199
    }

    # Запрос к апи
    response = requests.get('https://api.vk.com/method/stats.get', params=params)

    response_data = response.json()['response']

    # Инициализация заготовок
    likes, copies, hidden, comment, subscribed, unsubscribed, reach1, reach_subscribers, reach_unique_user = \
        ([], [], [], [], [], [], [], [], [])
    sex_f, sex_m = [], []
    age_data = {}
    age_sex_data = {}

    for item in response_data:
        activity = item.get("activity", {})
        reach = item.get("reach", {})
        likes.append(activity.get("likes", 0))
        copies.append(activity.get("copies", 0))
        hidden.append(activity.get("hidden", 0))
        comment.append(activity.get("comment", 0))
        subscribed.append(activity.get("subscribed", 0))
        unsubscribed.append(activity.get("unsubscribed", 0))
        reach1.append(reach.get("reach", 0))
        reach_subscribers.append(reach.get("reach_subscribers", 0))
        reach_unique_user. append(reach1[-1]-reach_subscribers[-1])

        for sex in reach.get("sex", []):
            if sex["value"] == "f":
                sex_f.append(sex["count"])
            elif sex["value"] == "m":
                sex_m.append(sex["count"])

        for age_group in reach.get("age", []):
            age_data[age_group["value"]] = age_group["count"]

        for sex_age in reach.get("sex_age", []):
            age_sex_data[sex_age["value"]] = sex_age["count"]

    sex_df = pd.DataFrame({"f": sex_f, "m": sex_m})
    age_df = pd.DataFrame(list(age_data.items()), columns=["age_group", "count"])
    age_sex_df = pd.DataFrame(list(age_sex_data.items()), columns=["sex_age", "count"])
    return (likes, copies, hidden, comment, subscribed, unsubscribed, reach1, reach_subscribers, reach_unique_user,
            sex_df, age_df, age_sex_df)
