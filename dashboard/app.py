from datetime import timedelta
import plotly.express as px
from google.cloud import bigquery
import streamlit as st
import pandas as pd
import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv()
# Ensure GOOGLE_APPLICATION_CREDENTIALS is set from .env
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Setup BigQuery client
client = bigquery.Client()

@st.cache_data(ttl=3600*6)  # cache 6 hours
def get_data():
    query = """
    SELECT * FROM `compnet-2206825965.news_analysis.sentiment_results`
    ORDER BY waktu DESC
    LIMIT 1000
    """
    df = client.query(query).to_dataframe()
    return df

# Load data
df = get_data()
df['waktu'] = pd.to_datetime(df['waktu'])

st.set_page_config(page_title="PSSI News Analysis Dashboard", layout="wide")

# Sidebar filters
with st.sidebar:
    st.title("PSSI News Analysis")
    st.header("⚙️ Settings")

    max_date = df['waktu'].max().date()
    min_date = df['waktu'].min().date()
    default_start_date = min_date
    default_end_date = max_date

    start_date = st.date_input("Start date", default_start_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", default_end_date, min_value=min_date, max_value=max_date)

    time_frame = st.selectbox("Select time frame", ("Daily", "Weekly", "Monthly", "Quarterly"))

# Filter data
filtered_df = df[(df['waktu'].dt.date >= start_date) & (df['waktu'].dt.date <= end_date)]

# --- Aggregation function --- #
def group_by_time(df, freq):
    if freq == "Daily":
        return df.groupby(pd.Grouper(key='waktu', freq='D'))
    elif freq == "Weekly":
        return df.groupby(pd.Grouper(key='waktu', freq='W'))
    elif freq == "Monthly":
        return df.groupby(pd.Grouper(key='waktu', freq='M'))
    elif freq == "Quarterly":
        return df.groupby(pd.Grouper(key='waktu', freq='Q'))
    else:
        return df

# Title
st.title("📊 PSSI News Sentiment Dashboard")

col1, col2 = st.columns(2)

# Time-series sentiment count
with col1:
    grouped = group_by_time(filtered_df, time_frame)
    sentiment_counts = grouped['sentiment'].value_counts().unstack().fillna(0)
    fig = px.line(sentiment_counts, x=sentiment_counts.index, y=sentiment_counts.columns,
                  labels={'value': 'Jumlah Berita', 'variable': 'Sentimen'},
                  title='Tren Sentimen Berita dari Waktu ke Waktu')
    st.plotly_chart(fig, use_container_width=True)

# Pie chart of sentiment distribution
with col2:
    sentiment_dist = filtered_df['sentiment'].value_counts().reset_index()
    sentiment_dist.columns = ['sentiment', 'count']  # rename biar kolomnya jelas
    fig2 = px.pie(sentiment_dist, values='count', names='sentiment',
                  title='Distribusi Sentimen Berita')
    st.plotly_chart(fig2, use_container_width=True)

# WordCloud
st.subheader("🗯️ Word Cloud Berita")
all_text = ' '.join(filtered_df['teks_cleaned'].dropna())
if all_text:
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
    fig_wc, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")

     # Layout 3 kolom: kiri - tengah (utama) - kanan
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.pyplot(fig_wc)
else:
    st.info("Tidak ada teks yang bisa dianalisis untuk Word Cloud dalam rentang waktu yang dipilih.")

# Top headlines
st.subheader("📰 5 Berita Terbaru")
latest_news = filtered_df.sort_values(by="waktu", ascending=False).head(5)

cols = st.columns(5)
for col, (_, row) in zip(cols, latest_news.iterrows()):
    with col:
        with st.container(border=True):
            st.caption(row['waktu'].date())
            st.markdown(f"**[{row['judul']}]({row['link']})**")
            st.markdown(f"*Sentimen:* `{row['sentiment']}`")

st.subheader("🟢 5 Berita Positif Terbaru")
positive_news = filtered_df[filtered_df['sentiment'] == 'positive'].sort_values(by='waktu', ascending=False).head(5)

cols = st.columns(5)
for col, (_, row) in zip(cols, positive_news.iterrows()):
    with col:
        with st.container(border=True):
            st.caption(row['waktu'].date())
            st.markdown(f"**[{row['judul']}]({row['link']})**")

st.subheader("🔴 5 Berita Negatif Terbaru")
negative_news = filtered_df[filtered_df['sentiment'] == 'negative'].sort_values(by='waktu', ascending=False).head(5)

cols = st.columns(5)
for col, (_, row) in zip(cols, negative_news.iterrows()):
    with col:
        with st.container(border=True):
            st.caption(row['waktu'].date())
            st.markdown(f"**[{row['judul']}]({row['link']})**")

# Sentiment breakdown over time (bar chart)
st.subheader("📈 Rangkuman Sentimen per Periode")
sent_per_period = sentiment_counts.reset_index().melt(id_vars='waktu', var_name='Sentimen', value_name='Jumlah')
fig3 = px.bar(sent_per_period, x='waktu', y='Jumlah', color='Sentimen', barmode='group',
              title=f"Jumlah Sentimen per {time_frame}")
st.plotly_chart(fig3, use_container_width=True)

# Optional export
st.download_button("📥 Download Data yang Difilter", filtered_df.to_csv(index=False), file_name='filtered_data.csv')

st.markdown("""
---
<div style="text-align: center; font-size: 14px; color: gray;">
    © 2025 | Made with ❤️ by 
    <a href="https://github.com/fathanadhitama/news-sentiment-app" target="_blank">
        Fathan Naufal Adhitama
    </a> • Data is ethically collected via web scraping from <a href="https://detik.com/">Detik.com</a>
</div>
""", unsafe_allow_html=True)

