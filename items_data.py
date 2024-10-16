import pandas as pd
import plotly.graph_objs as go
from get_data import access_token
from get_data import start_time, end_time, df, fetch_vk_stats, id_group
from strings import ar_mean_low, ar_mean_average, ar_mean_high, err_mean_high, err_mean_average, err_mean_low

# Перевод во временной промежуток (список) для построения графика
date_range = pd.date_range(start=pd.to_datetime(int(start_time), unit='s').date(),
                           end=pd.to_datetime(int(end_time), unit='s').date())

# Вызов функции, запись в переменные и постобработка данных
(likes, copies, hidden, comment, subscribed, unsubscribed, reach,
 reach_subscribers, reach_unique_user, sex_df, age_df, age_sex_df) = \
    (fetch_vk_stats(start_time, end_time, access_token, id_group))


# Данные для пола
def get_sex(sex_df):
    count_female = sum(sex_df['f'])
    count_male = sum(sex_df['m'])
    return count_female, count_male

# Топ-5 категорий по половозрастному составу
def top_5_age_sex_category(age_sex_df):
    age_sex_df = age_sex_df.sort_values(by=['count'], ascending=False)
    total_count = age_sex_df['count'].sum()
    top_5 = []
    for index, row in age_sex_df.iterrows():
        if row['count'] != 0 and len(top_5) < 5:
            sex, age = row['sex_age'].split(';')
            category = f"{ 'Мужчины' if sex == 'm' else 'Женщины' } {age} лет"
            percentage = round((row['count'] / total_count) * 100, 3)
            top_5.append((category, percentage))
    return top_5


top_5 = top_5_age_sex_category(age_sex_df)


# Данные для диаграммы возрастов
def get_age(age_df):
    age_12_21 = (age_df[(age_df['age_group'] == '12-18')]['count'].values[0]
                 + age_df[(age_df['age_group'] == '18-21')]['count'].values[0])
    age_21_27 = (age_df[(age_df['age_group'] == '21-24')]['count'].values[0]
                 + age_df[(age_df['age_group'] == '24-27')]['count'].values[0])
    age_27_30 = (age_df[(age_df['age_group'] == '27-30')]['count'].values[0]
                 + age_df[(age_df['age_group'] == '30-35')]['count'].values[0])
    age_35_45 = age_df[(age_df['age_group'] == '35-45')]['count'].values[0]
    age_45_100 = age_df[(age_df['age_group'] == '45-100')]['count'].values[0]
    return age_12_21, age_21_27, age_27_30, age_35_45, age_45_100


# Расчёт ERR
def calculate_err_mean(likes, copies, comment, reach):
    err_mean_calculated = ((sum(likes) + sum(copies) + sum(comment)) / sum(reach)) * 100
    return err_mean_calculated


err_mean = calculate_err_mean(likes, copies, comment, reach)


# Советы по повышению ERR
def get_text_advice_err(err_mean):
    if err_mean <= 1:
        return err_mean_low
    elif 1 < err_mean <= 3.5:
        return err_mean_average
    else:
        return err_mean_high


# Расчёт AR
def calculate_ar_mean(copies, reach):
    ar_mean_calculated = (sum(copies) / sum(reach)) * 100
    return ar_mean_calculated


ar_mean = calculate_ar_mean(copies, reach)


# Советы по повышению AR
def get_text_advice_ar(ar_mean):
    if ar_mean <= 1:
        return ar_mean_low
    elif 1 < ar_mean <= 5:
        return ar_mean_average
    else:
        return ar_mean_high


# Вычисление самого популярного поста
def find_most_popular_post(df, start_time, end_time, like_weight=0.5, view_weight=0.3, comment_weight=0.2):
    # Преобразование столбца Date_UNIX в числовой тип данных
    df['Date_UNIX'] = pd.to_numeric(df['Date_UNIX'], errors='coerce')

    # Преобразование start_time и end_time из str в int
    start_time = int(start_time)
    end_time = int(end_time)

    # Преобразование даты из UNIX-времени в datetime
    df['Date'] = pd.to_datetime(df['Date_UNIX'], unit='s')

    # Фильтрация данных по промежутку времени
    filtered_df = df[(df['Date_UNIX'] >= start_time) & (df['Date_UNIX'] <= end_time)]

    # Вычисление популярности постов
    filtered_df.loc[:, 'Popularity'] = (
            df['Likes'] * like_weight + df['Views'] * view_weight + df['Comments'] * comment_weight
    )

    # Определение самого популярного поста
    most_popular_post = filtered_df.loc[filtered_df['Popularity'].idxmax()]
    return most_popular_post


most_popular_post = find_most_popular_post(df, start_time, end_time,
                                           like_weight=0.5, view_weight=0.3, comment_weight=0.2)


# Метрика Engagement Rate by Post (ERP) за последнюю неделю
def calculate_erp(df):
    # Преобразование столбца 'Date_UNIX' в datetime
    df['Date'] = pd.to_datetime(df['Date_UNIX'], unit='s')

    # Фильтрация данных за последнюю неделю
    one_week_ago = pd.Timestamp.now() - pd.Timedelta(weeks=1)
    df_week = df[df['Date'] >= one_week_ago]

    # Вычисление ERP
    df_week['ERP'] = ((df_week['Likes'] + df_week['Comments'] + df_week['Reposts']) / df_week['Views']) * 100
    return df_week[['Text', 'ERP']].sort_values(by='ERP', ascending=False)


# Рост подписчиков (Daily Growth of Subscribers)
def calculate_daily_growth(subscribed, unsubscribed, date_range):
    daily_growth = [subscribed[i] - unsubscribed[i] for i in range(len(subscribed))]
    df_daily_growth = pd.DataFrame({'Date': date_range, 'Daily Growth': daily_growth})
    return df_daily_growth


# Частота постов (Post Frequency)
def calculate_post_frequency(df):
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
    post_frequency = df['Date'].dt.date.value_counts().sort_index()
    return post_frequency


# Построение dataframe для активности
data_activity = {
    "Date": date_range,
    "Likes": likes,
    "Comments": comment,
    "Reposts": copies
}

df_activity = pd.DataFrame(data_activity)
df_activity['Unix'] = df_activity['Date'].apply(lambda x: int(x.timestamp()))


# Построение графика активности
fig_activity = go.Figure()
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Likes'],
                                  mode='lines+markers', name='Likes'))
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Comments'],
                                  mode='lines+markers', name='Comments'))
fig_activity.add_trace(go.Scatter(x=df_activity['Date'], y=df_activity['Reposts'],
                                  mode='lines+markers', name='Reposts'))
fig_activity.update_layout(title='Activity', xaxis_title='Date', yaxis_title='Count')
fig_activity.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')


# Данные динамики пользователей: просмотры, подписки
data_dynamic = {
    "Date": date_range,
    "Reach subscribers":  reach_subscribers,
    "Reach unique": reach_unique_user
}

# Построение dataframe для динамики
df_dynamic = pd.DataFrame(data_dynamic)
df_dynamic['Unix'] = df_dynamic['Date'].apply(lambda x: int(x.timestamp()))


# Построение графика динамики пользователей
fig_dynamic = go.Figure()
fig_dynamic.add_trace(go.Scatter(x=df_dynamic['Date'], y=df_dynamic['Reach subscribers'],
                                 mode='lines+markers', name='Reach subscribers'))
fig_dynamic.add_trace(go.Scatter(x=df_dynamic['Date'], y=df_dynamic['Reach unique'],
                                 mode='lines+markers', name='Reach unique'))
fig_dynamic.update_layout(title='User Dynamics', xaxis_title='Date', yaxis_title='Count')
fig_dynamic.update_layout(plot_bgcolor='#39344a', paper_bgcolor='#39344a', font_color='#cbc2b9')


# Пол для круговой диаграммы
gender_list = list(get_sex(sex_df))

# Возраст для круговой диаграммы
age_list = list(get_age(age_df))

# Подготовка списка категорий целевой аудитории к выводу на экран
list_items = ""
for entry in top_5:
    list_items += f"<li style='color: #f9f9f9; font-size: 16px;'>{entry[0]} - {entry[1]:.3f}%</li>\n"

# Построение графиков и вывод данных ERP, Daily Growth, Post Frequency
erp_df = calculate_erp(df)
daily_growth_df = calculate_daily_growth(subscribed, unsubscribed, date_range)
post_frequency_df = calculate_post_frequency(df)