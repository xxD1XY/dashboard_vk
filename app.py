import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from get_data import df, fetch_vk_stats, start_time, end_time, id_group, access_token
from items_data import (
    fig_activity,
    fig_dynamic,
    get_sex,
    get_age,
    top_5_age_sex_category,
    most_popular_post,
    calculate_erp,
    calculate_daily_growth,
    calculate_post_frequency,
)

# Основной заголовок
st.title('VK Dashboard')

# Вызов функции fetch_vk_stats
(likes, copies, hidden, comment, subscribed, unsubscribed, reach,
 reach_subscribers, reach_unique_user, sex_df, age_df, age_sex_df) = fetch_vk_stats(start_time, end_time, access_token, id_group)

# Самый популярный пост с использованием expander
st.header('Самый популярный пост')
with st.expander("Показать детали самого популярного поста"):
    st.write("Text:", most_popular_post['Text'])
    st.write("Likes:", most_popular_post['Likes'])
    st.write("Comments:", most_popular_post['Comments'])
    st.write("Views:", most_popular_post['Views'])
    st.write("URL:", most_popular_post['URL'])


# График активности
st.subheader('График активности')
st.plotly_chart(fig_activity)

# График динамики пользователей
st.subheader('Динамика пользователей')
st.plotly_chart(fig_dynamic)

# Пол пользователей (круговая диаграмма)
st.subheader('Пол пользователей')
gender_counts = get_sex(sex_df)
fig_gender = go.Figure(data=[go.Pie(labels=['Female', 'Male'], values=gender_counts, hole=.4)])
st.plotly_chart(fig_gender)

# Возраст пользователей (круговая диаграмма)
st.subheader('Возраст пользователей')
age_counts = get_age(age_df)
fig_age = go.Figure(data=[go.Pie(labels=['12-21', '21-27', '27-30', '35-45', '45-100'], values=age_counts, hole=.4)])
st.plotly_chart(fig_age)

# Топ-5 категорий
st.subheader('Топ-5 категорий возраста')
top_5 = top_5_age_sex_category(age_sex_df)
for category, percentage in top_5:
    st.write(f"{category}: {percentage:.2f}%")

# Функция для сокращения текста до двух-трех слов
def shorten_text(text, max_words=3):
    words = text.split()
    return ' '.join(words[:max_words]) if len(words) > max_words else text

# Уровень вовлеченности (ERP)
st.subheader('Уровень вовлеченности (ERP)')
erp_df = calculate_erp(df)  # Вычисление ERP

# Сокращение текста постов
erp_df['Shortened Text'] = erp_df['Text'].apply(shorten_text)

# Построение графика ERP
fig_erp = go.Figure(data=[go.Bar(x=erp_df['Shortened Text'], y=erp_df['ERP'])])
fig_erp.update_layout(title='Уровень вовлеченности', xaxis_title='Post Text', yaxis_title='ERP (%)')
st.plotly_chart(fig_erp)


# Частота постов (Post Frequency)
st.subheader('Частота постов')
post_frequency_df = calculate_post_frequency(df)
st.bar_chart(post_frequency_df)

# --- Добавление новых графиков ---

# Среднее количество лайков, просмотров, репостов, комментариев и голосов по дням недели
st.subheader('Средние показатели по дням недели')

# Фильтрация только числовых столбцов
numeric_columns = df.select_dtypes(include=['number']).columns

# Группируем данные по дням недели и считаем средние значения только для числовых столбцов
data_days = df.groupby(df['Date'].dt.day_name())[numeric_columns].mean()

# Разделение на две колонки
col1, col2 = st.columns(2)

# Первая колонка - Лайки и Просмотры
with col1:
    # График для лайков
    fig_likes = go.Figure()
    fig_likes.add_trace(go.Scatter(x=data_days.index, y=data_days['Likes'], mode='lines', name='Likes'))
    fig_likes.update_layout(title='Среднее количество лайков по дням недели', xaxis_title='День недели', yaxis_title='Лайки')
    st.plotly_chart(fig_likes)

    # График для просмотров
    fig_views = go.Figure()
    fig_views.add_trace(go.Scatter(x=data_days.index, y=data_days['Views'], mode='lines', name='Views'))
    fig_views.update_layout(title='Среднее количество просмотров по дням недели', xaxis_title='День недели', yaxis_title='Просмотры')
    st.plotly_chart(fig_views)

# Вторая колонка - Репосты, Комментарии и Голоса
with col2:
    # График для репостов
    fig_reposts = go.Figure()
    fig_reposts.add_trace(go.Scatter(x=data_days.index, y=data_days['Reposts'], mode='lines', name='Reposts'))
    fig_reposts.update_layout(title='Среднее количество репостов по дням недели', xaxis_title='День недели', yaxis_title='Репосты')
    st.plotly_chart(fig_reposts)

    # График для комментариев
    fig_comments = go.Figure()
    fig_comments.add_trace(go.Scatter(x=data_days.index, y=data_days['Comments'], mode='lines', name='Comments'))
    fig_comments.update_layout(title='Среднее количество комментариев по дням недели', xaxis_title='День недели', yaxis_title='Комменты')
    st.plotly_chart(fig_comments)
