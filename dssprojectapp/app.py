import streamlit as st
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from datetime import datetime

# ------------------------------------------------------
# Page setup
# ------------------------------------------------------
st.set_page_config(page_title="Amazon Review Analysis", layout="wide", page_icon="🛒")
st.title(" Amazon Customer Feedback Dashboard")

# ------------------------------------------------------
# Sidebar
# ------------------------------------------------------
st.sidebar.header(" Upload & Settings")
uploaded_file = st.sidebar.file_uploader(
    "Upload your Amazon reviews CSV file",
    type=["csv"],
    help="Must contain columns like 'Score' and 'Text'"
)

# ------------------------------------------------------
# Load and process data
# ------------------------------------------------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f" Loaded {len(df)} reviews")

    with st.expander(" Data Preview"):
        st.dataframe(df.head(10))

    # Convert Time (UNIX) → datetime
    if 'Time' in df.columns:
        df['date'] = pd.to_datetime(df['Time'], unit='s')

    # Generate sentiment
    st.info(" Analyzing sentiment of reviews... please wait a few seconds")
    df['sentiment_score'] = df['Text'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    df['sentiment'] = df['sentiment_score'].apply(
        lambda x: 'Positive' if x > 0.1 else ('Negative' if x < -0.1 else 'Neutral')
    )

    # ------------------------------------------------------
    # Summary Metrics
    # ------------------------------------------------------
    st.subheader(" Summary Metrics")

    total_reviews = len(df)
    avg_rating = round(df['Score'].mean(), 2)
    sentiment_counts = df['sentiment'].value_counts()
    sentiment_pct = (sentiment_counts / total_reviews * 100).round(1)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Reviews", total_reviews)
    col2.metric("Average Rating", avg_rating)
    col3.metric("Positive (%)", f"{sentiment_pct.get('Positive', 0)}%")
    col4.metric("Negative (%)", f"{sentiment_pct.get('Negative', 0)}%")

    # ------------------------------------------------------
    # Dashboard Layout
    # ------------------------------------------------------
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 2])

    # Pie Chart
    with c1:
        fig_pie = px.pie(
            names=sentiment_counts.index,
            values=sentiment_counts.values,
            color=sentiment_counts.index,
            hole=0.4,
            title="Sentiment Breakdown"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Rating Distribution
    with c2:
        fig_bar = px.histogram(
            df,
            x='Score',
            color='sentiment',
            nbins=5,
            title="Ratings Distribution by Sentiment",
            barmode='group'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Recent Reviews
    with c3:
        st.write(" **Recent Reviews**")
        st.dataframe(df[['Summary', 'Text', 'sentiment', 'Score', 'date']].head(10), height=340)

    # ------------------------------------------------------
    # Trend Section
    # ------------------------------------------------------
    st.markdown("---")
    c4, c5 = st.columns(2)

    # Sentiment Trend Over Time
    with c4:
        if 'date' in df.columns:
            trend = df.groupby([df['date'].dt.to_period('M'), 'sentiment']).size().unstack(fill_value=0)
            trend.index = trend.index.to_timestamp()
            fig_line = px.line(
                trend,
                x=trend.index,
                y=trend.columns,
                title="Sentiment Trend Over Time"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info(" No 'Time' column found for trend visualization.")

    # Most Common Reviewers
    with c5:
        top_users = df['ProfileName'].value_counts().nlargest(10)
        fig_users = px.bar(
            x=top_users.values,
            y=top_users.index,
            orientation='h',
            title="Top 10 Reviewers",
            color=top_users.values,
            color_continuous_scale="Tealgrn"
        )
        st.plotly_chart(fig_users, use_container_width=True)

else:
    st.info(" Upload your Amazon reviews CSV in the sidebar to begin.")
